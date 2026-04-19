import re
import dns.resolver
from utils.logger import get_logger

logger = get_logger(__name__)

_SUSPICIOUS_TLDS = {'.xyz', '.top', '.click', '.loan', '.work', '.gq', '.tk', '.ml', '.cf', '.pw', '.icu'}
_BRAND_NAMES = ['paypal', 'amazon', 'google', 'microsoft', 'apple', 'netflix', 'facebook',
                'instagram', 'twitter', 'bank', 'chase', 'wellsfargo', 'citibank']


def _lookup(domain: str, record: str) -> list:
    try:
        answers = dns.resolver.resolve(domain, record, lifetime=3.0)
        return [str(r) for r in answers]
    except Exception:
        return []


def _clean_domain(raw: str) -> str:
    raw = raw.strip().lower()
    raw = re.sub(r'^https?://', '', raw)
    raw = raw.split('/')[0].split('?')[0]
    return raw


class DomainCheckerAgent:
    def analyze(self, raw_input: str) -> dict:
        logger.info("Starting domain check")
        domain = _clean_domain(raw_input.strip().splitlines()[0])

        if not re.match(r'^[a-z0-9\-\.]+\.[a-z]{2,}$', domain):
            return {
                "threat_level": "⚪ UNKNOWN",
                "confidence_score": 20,
                "recommendation": "Enter a valid domain name (e.g. example.com).",
                "summary": f"'{domain}' does not appear to be a valid domain.",
            }

        issues = []
        score = 0
        dns_info = {}

        # A records
        a_records = _lookup(domain, 'A')
        dns_info['A records'] = a_records if a_records else ['Not found']
        if not a_records:
            issues.append("No A record — domain does not resolve to an IP")
            score += 30

        # MX records
        mx_records = _lookup(domain, 'MX')
        dns_info['MX records'] = mx_records if mx_records else ['Not found']
        if not mx_records:
            issues.append("No MX record — domain has no mail server")
            score += 15

        # NS records
        ns_records = _lookup(domain, 'NS')
        dns_info['NS records'] = ns_records if ns_records else ['Not found']
        if not ns_records:
            issues.append("No NS record found")
            score += 20

        # Suspicious TLD
        tld = '.' + domain.rsplit('.', 1)[-1]
        if tld in _SUSPICIOUS_TLDS:
            issues.append(f"Suspicious TLD ({tld}) frequently used in scam domains")
            score += 35

        # Lookalike domain check
        for brand in _BRAND_NAMES:
            if brand in domain and f"{brand}.com" != domain and f"{brand}.org" != domain:
                issues.append(f"Possible {brand} impersonation domain")
                score += 45
                break

        # Hyphen abuse (many hyphens = suspicious)
        hyphen_count = domain.count('-')
        if hyphen_count >= 3:
            issues.append(f"Excessive hyphens in domain ({hyphen_count}) — common in phishing")
            score += 20

        # Very long domain
        base = domain.split('.')[0]
        if len(base) > 30:
            issues.append(f"Unusually long subdomain/name ({len(base)} chars)")
            score += 15

        # Numbers in domain (not purely numeric, but mixed — e.g. paypa1)
        if re.search(r'[a-z]\d[a-z]|\d[a-z]\d', domain):
            issues.append("Mixed letters and digits suggest character substitution")
            score += 25

        if score >= 70:
            threat_level = "🔴 CRITICAL"
            confidence = 91
            recommendation = "Very likely malicious domain. Do not visit or interact."
        elif score >= 40:
            threat_level = "🔴 HIGH"
            confidence = 83
            recommendation = "High-risk domain. Avoid and report to your security team."
        elif score >= 20:
            threat_level = "🟡 MEDIUM"
            confidence = 70
            recommendation = "Some suspicious signals. Verify before visiting."
        else:
            threat_level = "🟢 LOW"
            confidence = 87
            recommendation = "Domain appears legitimate based on available signals."

        indicators_text = "\n".join(f"  • {i}" for i in issues) if issues else "  • No suspicious indicators detected"

        dns_text = "\n".join(
            f"  {k}: {', '.join(v[:3])}" for k, v in dns_info.items()
        )

        summary = f"""DOMAIN REPUTATION CHECK

Domain: {domain}

DNS RECORDS:
{dns_text}

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
