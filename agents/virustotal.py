import base64
import hashlib
import time
import requests
from utils.logger import get_logger
import config

logger = get_logger(__name__)

VT_BASE = "https://www.virustotal.com/api/v3"
_TIMEOUT = 10


def _headers() -> dict:
    return {"x-apikey": config.VT_API_KEY, "Accept": "application/json"}


def _parse_stats(stats: dict, total_engines: int) -> dict:
    malicious   = stats.get("malicious", 0)
    suspicious  = stats.get("suspicious", 0)
    harmless    = stats.get("harmless", 0)
    undetected  = stats.get("undetected", 0)
    flagged     = malicious + suspicious
    scanned     = flagged + harmless + undetected

    if malicious >= 5 or (malicious >= 2 and flagged >= 4):
        risk = "critical"
    elif malicious >= 2 or flagged >= 4:
        risk = "high"
    elif malicious == 1 or suspicious >= 2:
        risk = "medium"
    else:
        risk = "low"

    return {
        "risk":        risk,
        "malicious":   malicious,
        "suspicious":  suspicious,
        "harmless":    harmless,
        "undetected":  undetected,
        "scanned":     scanned,
    }


# ── URL ───────────────────────────────────────────────────────────────────────

def scan_url(url: str) -> dict | None:
    """Look up a URL on VT. Returns parsed stats or None on error."""
    if not config.VT_API_KEY:
        return None
    try:
        url_id = base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")
        r = requests.get(f"{VT_BASE}/urls/{url_id}", headers=_headers(), timeout=_TIMEOUT)

        if r.status_code == 404:
            # Submit for scanning
            sub = requests.post(
                f"{VT_BASE}/urls",
                headers={**_headers(), "Content-Type": "application/x-www-form-urlencoded"},
                data=f"url={requests.utils.quote(url, safe='')}",
                timeout=_TIMEOUT,
            )
            if sub.status_code != 200:
                return None
            analysis_id = sub.json()["data"]["id"]
            time.sleep(3)
            r = requests.get(f"{VT_BASE}/analyses/{analysis_id}", headers=_headers(), timeout=_TIMEOUT)
            if r.status_code != 200:
                return None
            attrs = r.json()["data"]["attributes"]
            stats = attrs.get("stats", {})
        elif r.status_code == 200:
            attrs = r.json()["data"]["attributes"]
            stats = attrs.get("last_analysis_stats", {})
        else:
            logger.warning(f"VT URL lookup failed: {r.status_code}")
            return None

        total = sum(stats.values()) or 1
        result = _parse_stats(stats, total)
        result["permalink"] = f"https://www.virustotal.com/gui/url/{base64.urlsafe_b64encode(url.encode()).decode().rstrip('=')}"
        return result

    except Exception as e:
        logger.warning(f"VT URL error: {e}")
        return None


# ── File ──────────────────────────────────────────────────────────────────────

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_file(path: str) -> dict | None:
    """Look up file hash on VT; upload if not found. Returns parsed stats or None."""
    if not config.VT_API_KEY:
        return None
    try:
        sha = sha256_file(path)
        r = requests.get(f"{VT_BASE}/files/{sha}", headers=_headers(), timeout=_TIMEOUT)

        if r.status_code == 404:
            import os
            size = os.path.getsize(path)
            if size > 32 * 1024 * 1024:
                return {"error": "File too large for free VT upload (>32 MB)", "sha256": sha}

            with open(path, "rb") as fh:
                up = requests.post(
                    f"{VT_BASE}/files",
                    headers=_headers(),
                    files={"file": (os.path.basename(path), fh)},
                    timeout=60,
                )
            if up.status_code != 200:
                return None
            analysis_id = up.json()["data"]["id"]

            for _ in range(6):
                time.sleep(5)
                ar = requests.get(f"{VT_BASE}/analyses/{analysis_id}", headers=_headers(), timeout=_TIMEOUT)
                if ar.status_code == 200:
                    status = ar.json()["data"]["attributes"].get("status", "")
                    if status == "completed":
                        stats = ar.json()["data"]["attributes"].get("stats", {})
                        result = _parse_stats(stats, sum(stats.values()) or 1)
                        result["sha256"] = sha
                        result["permalink"] = f"https://www.virustotal.com/gui/file/{sha}"
                        return result
            return None

        elif r.status_code == 200:
            attrs = r.json()["data"]["attributes"]
            stats = attrs.get("last_analysis_stats", {})
            result = _parse_stats(stats, sum(stats.values()) or 1)
            result["sha256"] = sha
            result["permalink"] = f"https://www.virustotal.com/gui/file/{sha}"
            result["name"] = attrs.get("meaningful_name", "")
            result["type"] = attrs.get("type_description", "")
            return result
        else:
            logger.warning(f"VT file lookup: {r.status_code}")
            return None

    except Exception as e:
        logger.warning(f"VT file error: {e}")
        return None
