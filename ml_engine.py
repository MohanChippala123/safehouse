"""ML-based threat detection and pattern learning."""
import json
from collections import defaultdict
from typing import Any


class PatternDetector:
    """Detect attack patterns in analysis results."""

    PHISHING_PATTERNS = [
        r"login|auth|verify|confirm|update|secure",
        r"paypal|amazon|apple|google|microsoft",
        r"click here|act now|urgent|verify identity",
    ]

    MALWARE_PATTERNS = [
        r"executable|\.exe|\.dll|\.scr",
        r"trojan|ransomware|worm|virus",
        r"obfuscated|encrypted|packed",
    ]

    def __init__(self):
        self.threat_history = defaultdict(lambda: {"count": 0, "severity": 0})

    def analyze(self, chain: list, page_analysis: dict, deep: dict) -> dict:
        """Detect threats using pattern analysis."""
        threats = []
        confidence = 0

        # Check for phishing indicators
        flags = []
        for hop in chain:
            flags.extend(hop.get("flags", []))

        typo = deep.get("typosquat", {})
        if typo.get("matches"):
            threats.append({"type": "brand_impersonation", "confidence": 0.9, "detail": "Mimics known brand"})
            confidence += 0.9

        cred = deep.get("credentials", {})
        if cred.get("forms"):
            bad_forms = [f for f in cred.get("forms", []) if f.get("flags")]
            if bad_forms:
                threats.append({"type": "credential_theft", "confidence": 0.85, "detail": "Credential harvesting detected"})
                confidence += 0.85

        deob = deep.get("deobfuscation", {})
        if deob.get("suspicious"):
            threats.append({"type": "obfuscated_code", "confidence": 0.8, "detail": "Suspicious obfuscated code"})
            confidence += 0.8

        page = page_analysis or {}
        if page.get("miners"):
            threats.append({"type": "cryptomining", "confidence": 0.9, "detail": "Cryptocurrency miner detected"})
            confidence += 0.9

        return {
            "threats": threats,
            "threat_count": len(threats),
            "overall_confidence": min(confidence / max(1, len(threats)), 1.0),
            "threat_level": self._threat_level(confidence / max(1, len(threats)))
        }

    @staticmethod
    def _threat_level(confidence: float) -> str:
        if confidence >= 0.8:
            return "critical"
        elif confidence >= 0.6:
            return "high"
        elif confidence >= 0.4:
            return "medium"
        else:
            return "low"

    def update_patterns(self, result: dict) -> None:
        """Learn from new analysis results."""
        threats = result.get("threats", [])
        for threat in threats:
            self.threat_history[threat["type"]]["count"] += 1
            self.threat_history[threat["type"]]["severity"] = max(
                self.threat_history[threat["type"]]["severity"],
                threat.get("confidence", 0)
            )

    def get_threat_stats(self) -> dict:
        """Get threat statistics from learned patterns."""
        return dict(self.threat_history)


class AnomalyDetector:
    """Detect anomalies in domain/host behavior."""

    def __init__(self):
        self.baseline = {"avg_hop_count": 2, "avg_risk_score": 10}

    def detect(self, chain: list) -> dict:
        """Detect anomalies in redirect chain."""
        hop_count = len(chain)
        avg_risk = sum(h.get("risk_score", 0) for h in chain) / max(1, hop_count)

        anomalies = []
        if hop_count > 5:
            anomalies.append({"type": "excessive_redirects", "severity": "medium", "value": hop_count})

        if avg_risk > 50:
            anomalies.append({"type": "consistently_risky", "severity": "high", "value": avg_risk})

        has_https = any(h.get("scheme") == "https" for h in chain)
        if not has_https:
            anomalies.append({"type": "no_https", "severity": "high", "value": "unencrypted"})

        return {
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "is_anomalous": len(anomalies) > 0
        }
