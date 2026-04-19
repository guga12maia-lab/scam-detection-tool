import re
from utils.logger import get_logger

logger = get_logger(__name__)

# Known scam area codes / prefixes (US-focused, illustrative)
_SCAM_AREA_CODES = {
    '268', '284', '473', '664', '649', '767', '809', '829', '849',
    '876', '900', '976',  # premium rate
}

_SCAM_PATTERNS = [
    (r'\b(IRS|Revenue|Tax)\b', "Government agency impersonation (IRS/Tax)"),
    (r'\b(Social Security|SSA|SSN)\b', "Social Security impersonation"),
    (r'\b(Microsoft|Windows|Tech Support)\b', "Tech support scam keyword"),
    (r'\b(prize|winner|lottery|jackpot)\b', "Lottery/prize scam keyword"),
    (r'\b(warrant|arrest|legal action|lawsuit)\b', "Legal threat scam keyword"),
    (r'\b(grandma|grandpa|grandson|granddaughter)\b', "Family emergency scam keyword"),
    (r'\b(crypto|bitcoin|investment opportunity)\b', "Crypto/investment scam keyword"),
    (r'\b(gift card|iTunes|Google Play|wire transfer)\b', "Payment scam method"),
]


def _normalize_number(raw: str) -> str:
    digits = re.sub(r'\D', '', raw)
    if digits.startswith('1') and len(digits) == 11:
        digits = digits[1:]
    return digits


class CallerIDAgent:
    def analyze(self, raw_input: str) -> dict:
        logger.info("Starting caller ID check")

        # Extract phone number and optional context
        lines = raw_input.strip().splitlines()
        number_raw = lines[0].strip() if lines else raw_input.strip()
        context = ' '.join(lines[1:]).strip() if len(lines) > 1 else ''

        digits = _normalize_number(number_raw)
        issues = []
        score = 0

        # Validate format
        if len(digits) not in (10, 11):
            if len(digits) < 7:
                return {
                    "threat_level": "⚪ UNKNOWN",
                    "confidence_score": 30,
                    "recommendation": "Enter a valid phone number to analyze.",
                    "summary": f"Could not parse '{number_raw}' as a phone number.",
                }

        # Area code checks (10-digit US numbers)
        if len(digits) == 10:
            area = digits[:3]
            if area in _SCAM_AREA_CODES:
                issues.append(f"Area code {area} is associated with premium-rate/scam calls")
                score += 50

            # 900 / premium
            if digits.startswith('900') or digits.startswith('976'):
                issues.append("Premium-rate number (charges apply per minute)")
                score += 60

            # Spoofed neighbor numbers (same first 6 digits as victim common pattern)
            if digits[:3] in ('555',):
                issues.append("Fictitious/reserved number range (555-xxxx)")
                score += 20

        # Check context text for scam keywords
        ctx_lower = (context + ' ' + number_raw).lower()
        for pattern, label in _SCAM_PATTERNS:
            if re.search(pattern, ctx_lower, re.IGNORECASE):
                issues.append(label)
                score += 25

        # Repeated digit patterns (e.g. 1234567890, 0000000000)
        if re.match(r'(\d)\1{6,}', digits):
            issues.append("Repeated-digit pattern (likely spoofed/fake)")
            score += 40
        if digits in ('1234567890', '0987654321', '1111111111'):
            issues.append("Sequential/repeated number (fake)")
            score += 40

        # Determine risk
        if score >= 70:
            threat_level = "🔴 CRITICAL"
            confidence = 90
            recommendation = "DO NOT answer or call back. Block this number immediately."
        elif score >= 40:
            threat_level = "🔴 HIGH"
            confidence = 82
            recommendation = "High scam risk. Do not provide personal information."
        elif score >= 20:
            threat_level = "🟡 MEDIUM"
            confidence = 70
            recommendation = "Treat with caution. Verify caller identity independently."
        else:
            threat_level = "🟢 LOW"
            confidence = 85
            recommendation = "No strong scam indicators found. Stay alert."

        fmt = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}" if len(digits) == 10 else number_raw
        indicators_text = "\n".join(f"  • {i}" for i in issues) if issues else "  • No known scam indicators"

        summary = f"""CALLER ID ANALYSIS

Number: {fmt}
{'Context provided: ' + context if context else ''}

RISK INDICATORS:
{indicators_text}

SCORE: {score}/100

RECOMMENDATION:
{recommendation}
"""
        return {
            "threat_level": threat_level,
            "confidence_score": confidence,
            "recommendation": recommendation,
            "summary": summary,
        }
