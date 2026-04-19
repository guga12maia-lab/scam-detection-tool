from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

_THREAT_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "unknown": 0}


def _parse_threat(verdict_text: str) -> str:
    low = verdict_text.lower()
    if "critical" in low: return "CRITICAL"
    if "high" in low:     return "HIGH"
    if "medium" in low:   return "MEDIUM"
    if "low" in low:      return "LOW"
    return "UNKNOWN"


class ReportGeneratorAgent:
    def analyze(self, raw_input: str) -> dict:
        logger.info("Generating security report")
        text = raw_input.strip()

        if not text:
            return {
                "threat_level": "⚪ UNKNOWN",
                "confidence_score": 0,
                "recommendation": "Paste analysis results or describe the incident.",
                "summary": "No input provided.",
            }

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = text.splitlines()

        # Extract any threat levels mentioned
        found_threats = []
        for line in lines:
            t = _parse_threat(line)
            if t != "UNKNOWN":
                found_threats.append(t)

        # Determine overall severity
        severity_rank = max((_THREAT_ORDER.get(t.lower(), 0) for t in found_threats), default=0)
        severity_map = {4: "CRITICAL", 3: "HIGH", 2: "MEDIUM", 1: "LOW", 0: "INFORMATIONAL"}
        overall = severity_map[severity_rank]

        threat_emoji = {
            "CRITICAL": "🔴", "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢", "INFORMATIONAL": "⚪"
        }.get(overall, "⚪")

        if overall in ("CRITICAL", "HIGH"):
            threat_level = f"🔴 {overall}"
            confidence = 88
            recommendation = "Immediate action required. Escalate to security team."
        elif overall == "MEDIUM":
            threat_level = "🟡 MEDIUM"
            confidence = 75
            recommendation = "Review findings and apply mitigations."
        elif overall == "LOW":
            threat_level = "🟢 LOW"
            confidence = 85
            recommendation = "Monitor situation. No immediate action required."
        else:
            threat_level = "⚪ INFORMATIONAL"
            confidence = 60
            recommendation = "Keep this report for records."

        word_count = len(text.split())
        line_count = len(lines)

        report = f"""SECURITY INCIDENT REPORT
Generated: {now}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXECUTIVE SUMMARY
Overall Severity: {threat_emoji} {overall}
Report based on: {line_count} lines | {word_count} words of input

{('THREATS IDENTIFIED: ' + ', '.join(set(found_threats))) if found_threats else 'No explicit threat levels detected in input.'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INCIDENT DETAILS

{text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDED ACTIONS

{recommendation}

1. Document all indicators of compromise (IOCs)
2. Preserve evidence (screenshots, logs, headers)
3. Notify affected parties if personal data involved
4. Block identified malicious domains, IPs, and numbers
5. Update security controls to prevent recurrence

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Report ID: SA-{datetime.now().strftime('%Y%m%d%H%M%S')}
"""
        return {
            "threat_level": threat_level,
            "confidence_score": confidence,
            "recommendation": recommendation,
            "summary": report,
        }
