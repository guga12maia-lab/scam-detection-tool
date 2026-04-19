import re
from utils.logger import get_logger

logger = get_logger(__name__)

_SHORTENERS = ['bit.ly', 'tinyurl', 't.co', 'ow.ly', 'is.gd', 'buff.ly', 'tiny.cc', 'cutt.ly']

_URGENCY = [
    'urgent', 'immediately', 'act now', 'expires', 'last chance', 'final notice',
    'suspended', 'locked', 'compromised', 'unauthorized', 'alert', 'warning',
]

_CREDENTIAL_REQUESTS = [
    'verify', 'confirm', 'update your', 'enter your', 'click here', 'click the link',
    'login', 'sign in', 'account details', 'bank details', 'credit card', 'pin',
    'ssn', 'social security', 'password',
]

_PRIZE_SCAM = [
    'congratulations', 'you have won', 'winner', 'prize', 'lottery', 'reward',
    'free gift', 'claim your', 'selected', 'lucky',
]

_DELIVERY_SCAM = [
    'package', 'delivery', 'parcel', 'shipment', 'tracking', 'usps', 'fedex',
    'ups', 'dhl', 'customs fee', 'redelivery',
]


class SMSDetectorAgent:
    def analyze(self, raw_input: str) -> dict:
        logger.info("Starting SMS analysis")
        text = raw_input.strip()
        lower = text.lower()

        issues = []
        score = 0

        # Urgency
        urgency_found = [w for w in _URGENCY if w in lower]
        if len(urgency_found) >= 3:
            issues.append(f"High urgency language ({len(urgency_found)} instances)")
            score += 35
        elif urgency_found:
            issues.append(f"Urgency language: {', '.join(urgency_found[:2])}")
            score += 20

        # Credential requests
        cred_found = [w for w in _CREDENTIAL_REQUESTS if w in lower]
        if cred_found:
            issues.append(f"Credential/action request: {', '.join(cred_found[:3])}")
            score += 40

        # Prize/lottery scam
        prize_found = [w for w in _PRIZE_SCAM if w in lower]
        if len(prize_found) >= 2:
            issues.append(f"Prize/lottery scam language: {', '.join(prize_found[:2])}")
            score += 45
        elif prize_found:
            issues.append(f"Possible prize scam keyword: {prize_found[0]}")
            score += 20

        # Fake delivery scam
        delivery_found = [w for w in _DELIVERY_SCAM if w in lower]
        if delivery_found and cred_found:
            issues.append("Delivery notification + credential request (common smishing)")
            score += 40
        elif len(delivery_found) >= 2:
            issues.append("Delivery scam pattern detected")
            score += 15

        # URL shorteners
        for s in _SHORTENERS:
            if s in lower:
                issues.append(f"URL shortener detected ({s})")
                score += 30
                break

        # HTTP links
        http_links = re.findall(r'http://\S+', text)
        if http_links:
            issues.append(f"Unencrypted link(s) (HTTP): {http_links[0][:50]}")
            score += 25

        # Phone number in suspicious context
        phone_in_text = re.search(r'\b\d{3}[\s\-\.]\d{3}[\s\-\.]\d{4}\b', text)
        if phone_in_text and cred_found:
            issues.append("Phone number with credential request")
            score += 20

        # Excessive CAPS
        caps_words = re.findall(r'\b[A-Z]{3,}\b', text)
        if len(caps_words) > 4:
            issues.append(f"Excessive capitalization ({len(caps_words)} all-caps words)")
            score += 10

        # Short message with link only (classic smishing)
        words = text.split()
        has_url = bool(re.search(r'https?://', text))
        if has_url and len(words) <= 15:
            issues.append("Short message with link only (common smishing pattern)")
            score += 20

        if score >= 70:
            threat_level = "🔴 CRITICAL"
            confidence = 93
            recommendation = "SMISHING DETECTED. Delete immediately. Do NOT click any links."
        elif score >= 45:
            threat_level = "🔴 HIGH"
            confidence = 85
            recommendation = "Very suspicious. Do not click links or reply."
        elif score >= 20:
            threat_level = "🟡 MEDIUM"
            confidence = 72
            recommendation = "Exercise caution. Verify sender via official channels."
        else:
            threat_level = "🟢 LOW"
            confidence = 88
            recommendation = "No strong smishing indicators. Stay vigilant."

        indicators_text = "\n".join(f"  • {i}" for i in issues) if issues else "  • No major smishing indicators"

        summary = f"""SMS / SMISHING ANALYSIS

Message length: {len(text)} characters | Words: {len(text.split())}

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
