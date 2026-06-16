"""Advanced features: batch analysis, export, history."""
import csv
import json
from io import StringIO
from datetime import datetime
from typing import Any


class BatchAnalyzer:
    """Analyze multiple URLs in batch mode."""

    def __init__(self, urls: list[str], max_workers: int = 3):
        self.urls = urls
        self.max_workers = max_workers
        self.results = []

    async def analyze_batch(self, session) -> list[dict]:
        """Analyze URLs concurrently."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import requests

        def analyze_one(url: str) -> dict:
            try:
                resp = requests.post("http://localhost:5000/analyze/chain", json={"url": url}, timeout=30)
                if resp.status_code == 200:
                    return {"url": url, "status": "success", "data": resp.json()}
                return {"url": url, "status": "error", "error": f"HTTP {resp.status_code}"}
            except Exception as e:
                return {"url": url, "status": "error", "error": str(e)}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(analyze_one, url): url for url in self.urls}
            for future in as_completed(futures):
                self.results.append(future.result())

        return self.results


class ResultExporter:
    """Export analysis results in multiple formats."""

    def __init__(self, results: list[dict]):
        self.results = results
        self.timestamp = datetime.now().isoformat()

    def to_json(self) -> str:
        """Export as JSON."""
        return json.dumps({
            "exported": self.timestamp,
            "count": len(self.results),
            "results": self.results
        }, indent=2)

    def to_csv(self) -> str:
        """Export as CSV."""
        if not self.results:
            return ""

        output = StringIO()
        fieldnames = ["url", "risk_level", "risk_score", "overall_risk", "timestamp"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for result in self.results:
            data = result.get("data", {})
            chain = data.get("chain", [])
            writer.writerow({
                "url": result.get("url", ""),
                "risk_level": chain[-1].get("risk_level", "unknown") if chain else "unknown",
                "risk_score": chain[-1].get("risk_score", 0) if chain else 0,
                "overall_risk": data.get("overall_risk", 0),
                "timestamp": self.timestamp
            })

        return output.getvalue()

    def to_html_report(self) -> str:
        """Export as HTML report."""
        html = f"""
        <html>
        <head>
            <title>SafeHouse Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .high {{ color: red; }}
                .medium {{ color: orange; }}
                .low {{ color: yellow; }}
                .clean {{ color: green; }}
            </style>
        </head>
        <body>
            <h1>SafeHouse Analysis Report</h1>
            <p>Generated: {self.timestamp}</p>
            <p>Total URLs analyzed: {len(self.results)}</p>
            <table>
                <tr>
                    <th>URL</th>
                    <th>Risk Level</th>
                    <th>Risk Score</th>
                    <th>Status</th>
                </tr>
        """

        for result in self.results:
            data = result.get("data", {})
            chain = data.get("chain", [])
            risk_level = chain[-1].get("risk_level", "unknown") if chain else "unknown"
            risk_score = chain[-1].get("risk_score", 0) if chain else 0
            html += f"""
                <tr>
                    <td>{result.get("url", "")}</td>
                    <td class="{risk_level}">{risk_level.upper()}</td>
                    <td>{risk_score}</td>
                    <td>{result.get("status", "")}</td>
                </tr>
            """

        html += """
            </table>
        </body>
        </html>
        """
        return html
