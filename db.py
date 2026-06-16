"""Database models and operations for SafeHouse."""
import sqlite3
import json
from datetime import datetime
from pathlib import Path


DB_PATH = Path(__file__).parent / "safehouse.db"


def init_db():
    """Initialize database with schema."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY,
            url TEXT UNIQUE,
            risk_level TEXT,
            risk_score INTEGER,
            overall_risk INTEGER,
            analysis_data TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS file_analyses (
            id INTEGER PRIMARY KEY,
            filename TEXT,
            file_hash TEXT UNIQUE,
            risk_score INTEGER,
            metadata TEXT,
            created_at TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS threats (
            id INTEGER PRIMARY KEY,
            analysis_id INTEGER,
            threat_type TEXT,
            severity TEXT,
            description TEXT,
            FOREIGN KEY(analysis_id) REFERENCES analyses(id)
        )
    """)

    c.execute("CREATE INDEX IF NOT EXISTS idx_url ON analyses(url)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_risk ON analyses(risk_level)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_created ON analyses(created_at)")

    conn.commit()
    conn.close()


class AnalysisDB:
    """Database operations for analyses."""

    @staticmethod
    def save_analysis(url: str, analysis: dict) -> int:
        """Save URL analysis result."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        chain = analysis.get("chain", [])
        risk_level = chain[-1].get("risk_level", "unknown") if chain else "unknown"
        risk_score = chain[-1].get("risk_score", 0) if chain else 0

        try:
            c.execute("""
                INSERT OR REPLACE INTO analyses
                (url, risk_level, risk_score, overall_risk, analysis_data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                url,
                risk_level,
                risk_score,
                analysis.get("overall_risk", 0),
                json.dumps(analysis),
                datetime.now(),
                datetime.now()
            ))
            conn.commit()
            return c.lastrowid
        finally:
            conn.close()

    @staticmethod
    def get_analysis(url: str) -> dict | None:
        """Retrieve saved analysis."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        try:
            c.execute("SELECT analysis_data, created_at FROM analyses WHERE url = ?", (url,))
            row = c.fetchone()
            if row:
                return {
                    "data": json.loads(row[0]),
                    "created_at": row[1],
                    "cached": True
                }
            return None
        finally:
            conn.close()

    @staticmethod
    def get_high_risk(limit: int = 10) -> list[dict]:
        """Get high-risk URLs from history."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        try:
            c.execute("""
                SELECT url, risk_level, risk_score, created_at
                FROM analyses
                WHERE risk_level IN ('high', 'medium')
                ORDER BY risk_score DESC
                LIMIT ?
            """, (limit,))
            return [
                {
                    "url": row[0],
                    "risk_level": row[1],
                    "risk_score": row[2],
                    "created_at": row[3]
                }
                for row in c.fetchall()
            ]
        finally:
            conn.close()

    @staticmethod
    def get_statistics() -> dict:
        """Get analysis statistics."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        try:
            c.execute("SELECT COUNT(*) FROM analyses")
            total = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM analyses WHERE risk_level = ?", ("high",))
            high = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM analyses WHERE risk_level = ?", ("medium",))
            medium = c.fetchone()[0]

            c.execute("SELECT AVG(risk_score) FROM analyses")
            avg_score = c.fetchone()[0] or 0

            return {
                "total_analyses": total,
                "high_risk": high,
                "medium_risk": medium,
                "average_score": round(avg_score, 2)
            }
        finally:
            conn.close()
