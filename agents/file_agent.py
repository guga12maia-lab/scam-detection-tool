import os
import hashlib
import re
from agents.virustotal import scan_file, sha256_file
from utils.logger import get_logger
import config

logger = get_logger(__name__)

_DANGEROUS_EXTS = {
    '.exe', '.dll', '.bat', '.cmd', '.vbs', '.js', '.jse', '.wsf', '.wsh',
    '.ps1', '.psm1', '.psd1', '.scr', '.com', '.pif', '.lnk', '.hta',
    '.msi', '.msp', '.reg', '.jar',
}
_DOUBLE_EXT = re.compile(r'\.(pdf|doc|docx|xls|xlsx|jpg|png|mp4)\.(exe|bat|cmd|vbs|js|scr)$', re.I)
_MAX_SAFE_SIZE = 100 * 1024 * 1024  # 100 MB


def _static_analysis(path: str) -> tuple[int, list[str]]:
    """Simple static checks that don't need VT."""
    issues = []
    score = 0
    name = os.path.basename(path)
    _, ext = os.path.splitext(name.lower())
    size = os.path.getsize(path)

    if ext in _DANGEROUS_EXTS:
        issues.append(f"Executable/script file type ({ext})")
        score += 40

    if _DOUBLE_EXT.search(name):
        issues.append("Double extension — disguised file type")
        score += 50

    if size == 0:
        issues.append("Empty file")
        score += 10
    elif size > _MAX_SAFE_SIZE:
        issues.append(f"Very large file ({size // (1024*1024)} MB)")
        score += 5

    # Check for hidden extension via Unicode tricks
    if '\u202e' in name or '\u200b' in name:
        issues.append("Unicode direction/zero-width character in filename")
        score += 60

    return score, issues


class FileCheckerAgent:
    def analyze(self, file_path: str) -> dict:
        logger.info(f"Starting file check: {file_path}")
        file_path = file_path.strip().strip('"')

        if not os.path.isfile(file_path):
            return {
                "threat_level": "⚪ UNKNOWN",
                "confidence_score": 0,
                "recommendation": "File not found. Check the path and try again.",
                "summary": f"File not found: {file_path}",
            }

        name = os.path.basename(file_path)
        size = os.path.getsize(file_path)
        size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024*1024):.1f} MB"

        # Static analysis
        h_score, h_issues = _static_analysis(file_path)

        # Compute hash
        try:
            sha = sha256_file(file_path)
        except Exception as e:
            sha = "error"
            h_issues.append(f"Could not hash file: {e}")

        # VirusTotal
        use_vt = bool(config.VT_API_KEY)
        vt = scan_file(file_path) if use_vt else None

        report_lines = [
            f"FILE ANALYSIS — {'VirusTotal + static' if use_vt else 'Static analysis (no VT key)'}\n",
            f"File:   {name}",
            f"Size:   {size_str}",
            f"SHA256: {sha[:32]}…{sha[-8:] if len(sha) > 40 else sha}\n",
        ]

        if vt:
            if "error" in vt:
                report_lines.append(f"VirusTotal: {vt['error']}\n")
                vt_risk = "low"
            else:
                mal, sus = vt["malicious"], vt["suspicious"]
                scanned = vt["scanned"]
                vt_risk = vt["risk"]
                report_lines.append(f"VIRUSTOTAL RESULTS:")
                report_lines.append(f"  {mal} malicious  |  {sus} suspicious  |  {scanned} engines scanned")
                if vt.get("name"):
                    report_lines.append(f"  Known as: {vt['name']}")
                if vt.get("type"):
                    report_lines.append(f"  Type: {vt['type']}")
                if vt.get("permalink"):
                    report_lines.append(f"  Full report: {vt['permalink']}")
                report_lines.append("")
        else:
            vt_risk = "low"
            report_lines.append("VirusTotal: no API key set — add key in Settings for cloud scan.\n")

        if h_issues:
            report_lines.append("STATIC ANALYSIS FLAGS:")
            for issue in h_issues:
                report_lines.append(f"  • {issue}")
            report_lines.append("")

        # Determine overall risk
        vt_score = {"critical": 90, "high": 70, "medium": 40, "low": 10, "error": 0}.get(vt_risk, 0)
        final_score = max(h_score, vt_score)

        if final_score >= 70 or (vt and vt.get("malicious", 0) >= 3):
            threat_level = "🔴 CRITICAL"
            confidence = 95 if use_vt else 75
            rec = "MALICIOUS FILE DETECTED. Do not open. Delete and report immediately."
        elif final_score >= 40 or (vt and vt.get("malicious", 0) >= 1):
            threat_level = "🔴 HIGH"
            confidence = 88 if use_vt else 70
            rec = "High-risk file. Do not open or execute."
        elif final_score >= 20:
            threat_level = "🟡 MEDIUM"
            confidence = 72
            rec = "Suspicious indicators found. Proceed with caution."
        else:
            threat_level = "🟢 LOW"
            confidence = 90 if use_vt else 60
            rec = "No threats detected." if use_vt else "No static flags. Add VT key for cloud verification."

        report_lines.append(f"RECOMMENDATION:\n{rec}")

        return {
            "threat_level": threat_level,
            "confidence_score": confidence,
            "recommendation": rec,
            "summary": "\n".join(report_lines),
        }
