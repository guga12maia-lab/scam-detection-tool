import re
from agents.virustotal import scan_url
from utils.logger import get_logger
import config

logger = get_logger(__name__)

_SHORTENERS = [
    'bit.ly', 'tinyurl.com', 't.co', 'ow.ly', 'is.gd', 'buff.ly',
    'adf.ly', 'goo.gl', 'shorte.st', 'tiny.cc', 'cutt.ly',
]
_SUSPICIOUS_TLDS = {'.xyz', '.top', '.click', '.loan', '.work', '.gq', '.tk', '.ml', '.cf', '.pw', '.icu'}
_PHISHING_WORDS = [
    'login', 'verify', 'secure', 'account', 'update', 'confirm',
    'banking', 'paypal', 'amazon', 'apple', 'microsoft', 'google',
    'password', 'credential', 'signin', 'wallet', 'suspend',
]


def _heuristic_score(url: str) -> tuple[int, list[str]]:
    url_lower = url.lower().strip()
    issues = []
    score = 0

    if url_lower.startswith('http://'):
        issues.append("Unencrypted connection (HTTP)")
        score += 20
    if re.search(r'https?://(\d{1,3}\.){3}\d{1,3}', url_lower):
        issues.append("IP address instead of domain name")
        score += 40
    for s in _SHORTENERS:
        if s in url_lower:
            issues.append(f"URL shortener ({s})")
            score += 30
            break
    try:
        from urllib.parse import urlparse
        host = urlparse(url if url_lower.startswith('http') else 'http://' + url).hostname or ''
        tld = '.' + host.rsplit('.', 1)[-1] if '.' in host else ''
        if tld in _SUSPICIOUS_TLDS:
            issues.append(f"Suspicious TLD ({tld})")
            score += 25
        if len(host.split('.')) > 4:
            issues.append(f"Excessive subdomains")
            score += 20
    except Exception:
        pass
    phish_found = [w for w in _PHISHING_WORDS if w in url_lower]
    if len(phish_found) >= 2:
        issues.append(f"Phishing keywords: {', '.join(phish_found[:3])}")
        score += 35
    elif phish_found:
        issues.append(f"Phishing keyword: {phish_found[0]}")
        score += 15
    if re.search(r'0x[0-9a-f]{4,}', url_lower):
        issues.append("Hex-encoded URL segment")
        score += 30
    if url.count('%') > 5:
        issues.append("Heavy percent-encoding")
        score += 25
    if len(url) > 200:
        issues.append(f"Unusually long URL ({len(url)} chars)")
        score += 10
    return score, issues


class URLScannerAgent:
    def analyze(self, raw_input: str) -> dict:
        logger.info("Starting URL scan")
        urls = [u.strip() for u in re.split(r'[\n\r,]+', raw_input) if u.strip() and '.' in u][:10]

        if not urls:
            return {
                "threat_level": "🟢 LOW",
                "confidence_score": 100,
                "recommendation": "No valid URLs detected.",
                "summary": "No URLs found to analyze.",
            }

        use_vt = bool(config.VT_API_KEY)
        report_lines = [
            f"URL SCAN — {len(urls)} URL(s)  |  {'VirusTotal + heuristics' if use_vt else 'Heuristic analysis (no VT key)'}\n"
        ]

        max_score = 0
        any_vt_high = False

        for url in urls:
            h_score, h_issues = _heuristic_score(url)
            vt = scan_url(url) if use_vt else None

            # Determine per-URL risk
            if vt:
                risk = vt["risk"]
                mal, sus = vt["malicious"], vt["suspicious"]
                scanned = vt["scanned"]
                vt_line = f"   VirusTotal: {mal} malicious, {sus} suspicious / {scanned} engines"
                if risk in ("high", "critical"):
                    any_vt_high = True
                # Blend: VT takes priority
                final_score = max(h_score, {"critical": 90, "high": 70, "medium": 40, "low": 10}[risk])
            else:
                risk = ("critical" if h_score >= 70 else "high" if h_score >= 40 else "medium" if h_score >= 20 else "low")
                vt_line = "   VirusTotal: no key set — heuristics only"
                final_score = h_score

            max_score = max(max_score, final_score)
            emoji = {"low": "✅", "medium": "⚠️", "high": "❌", "critical": "🚨"}.get(risk, "•")
            report_lines.append(f"{emoji} {url}")
            report_lines.append(f"   Risk: {risk.upper()}")
            if use_vt:
                report_lines.append(vt_line)
                if vt and vt.get("permalink"):
                    report_lines.append(f"   Full report: {vt['permalink']}")
            for issue in h_issues:
                report_lines.append(f"   • {issue}")
            report_lines.append("")

        if any_vt_high or max_score >= 70:
            threat_level = "🔴 CRITICAL"
            confidence = 95
            rec = "DO NOT visit these URLs. Block and report immediately."
        elif max_score >= 40:
            threat_level = "🔴 HIGH"
            confidence = 87
            rec = "Avoid clicking. Verify URLs through official channels."
        elif max_score >= 20:
            threat_level = "🟡 MEDIUM"
            confidence = 75
            rec = "Use caution. Confirm URL legitimacy before visiting."
        else:
            threat_level = "🟢 LOW"
            confidence = 90
            rec = "URLs appear safe. Stay alert."

        report_lines.append(f"RECOMMENDATION:\n{rec}")

        return {
            "threat_level": threat_level,
            "confidence_score": confidence,
            "recommendation": rec,
            "summary": "\n".join(report_lines),
        }
