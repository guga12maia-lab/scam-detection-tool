import requests
import dns.resolver
import re
from typing import Any
from utils.logger import get_logger

logger = get_logger(__name__)

class PhishingTools:
    """Tools for phishing email analysis"""
    
    @staticmethod
    def check_domain_reputation(domain: str) -> dict:
        """Check if domain is legitimate"""
        try:
            # Try to resolve domain
            dns.resolver.resolve(domain, 'MX')
            return {
                "tool": "domain_check",
                "domain": domain,
                "status": "resolvable",
                "risk_level": "low"
            }
        except Exception as e:
            logger.warning(f"Domain check failed for {domain}: {str(e)}")
            return {
                "tool": "domain_check",
                "domain": domain,
                "status": "unresolvable",
                "risk_level": "high",
                "error": str(e)
            }
    
    @staticmethod
    def check_urls(urls: list) -> dict:
        """Check URLs for suspicious patterns"""
        findings = []
        suspicious_patterns = [
            r'bit\.ly',  # URL shorteners
            r'tinyurl',
            r'0x[0-9a-f]+',  # Hex encoding in URLs
            r'%[0-9a-f]{2}',  # Percent encoding
        ]
        
        for url in urls:
            risk = "low"
            issues = []
            
            # Check for suspicious patterns
            for pattern in suspicious_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    risk = "high"
                    issues.append(f"Suspicious pattern: {pattern}")
            
            # Check for common phishing patterns
            if "login" in url.lower() or "verify" in url.lower():
                if not url.startswith("https"):
                    risk = "high"
                    issues.append("Unencrypted login/verify URL")
            
            findings.append({
                "url": url,
                "risk_level": risk,
                "issues": issues
            })
        
        return {
            "tool": "url_check",
            "total_urls": len(urls),
            "findings": findings,
            "overall_risk": "high" if any(f["risk_level"] == "high" for f in findings) else "low"
        }
    
    @staticmethod
    def analyze_urgency_indicators(text: str) -> dict:
        """Detect urgency and pressure tactics"""
        urgency_keywords = [
            "urgent", "immediately", "act now", "verify", "confirm",
            "update", "suspend", "locked", "compromise", "alert",
            "required", "action required", "time sensitive", "expires"
        ]
        
        pressure_keywords = [
            "click here", "verify account", "confirm identity", 
            "unusual activity", "suspicious", "unauthorized"
        ]
        
        urgency_count = sum(1 for word in urgency_keywords if word in text.lower())
        pressure_count = sum(1 for word in pressure_keywords if word in text.lower())
        
        risk_level = "low"
        if urgency_count >= 3 or pressure_count >= 2:
            risk_level = "high"
        elif urgency_count >= 1 or pressure_count >= 1:
            risk_level = "medium"
        
        return {
            "tool": "urgency_analysis",
            "urgency_keywords_found": urgency_count,
            "pressure_keywords_found": pressure_count,
            "risk_level": risk_level,
            "found_keywords": [w for w in urgency_keywords + pressure_keywords if w in text.lower()]
        }
    
    @staticmethod
    def check_sender_spoofing(sender: str, subject: str) -> dict:
        """Check for sender spoofing indicators"""
        issues = []
        risk_level = "low"
        
        # Check for generic greetings
        if "dear user" in subject.lower() or "dear customer" in subject.lower():
            issues.append("Generic greeting detected")
            risk_level = "medium"
        
        # Check for suspicious sender patterns
        if sender.count('@') > 1:
            issues.append("Multiple @ symbols in sender")
            risk_level = "high"
        
        if '..' in sender:
            issues.append("Double dots in sender")
            risk_level = "high"
        
        # Check for lookalike domains
        known_companies = ['apple', 'amazon', 'google', 'microsoft', 'paypal', 'bank']
        sender_domain = sender.split('@')[-1] if '@' in sender else sender
        
        for company in known_companies:
            if company in sender_domain.lower():
                # Check if it's the real domain
                if f"{company}.com" not in sender_domain.lower():
                    issues.append(f"Lookalike domain for {company}")
                    risk_level = "high"
        
        return {
            "tool": "spoofing_check",
            "sender": sender,
            "risk_level": risk_level,
            "issues": issues
        }
    
    @staticmethod
    def detect_grammar_quality(text: str) -> dict:
        """Detect grammar and quality issues (simple heuristics)"""
        issues = []
        risk_level = "low"
        
        # Check for multiple consecutive spaces
        if "  " in text:
            issues.append("Multiple consecutive spaces")
        
        # Check for unusual capitalization
        all_caps_words = len(re.findall(r'\b[A-Z]{3,}\b', text))
        if all_caps_words > 5:
            issues.append(f"Excessive all-caps words ({all_caps_words})")
            risk_level = "medium"
        
        # Check for common typos/misspellings
        typos = ['recieve', 'seperate', 'occured', 'untill', 'definately']
        typo_count = sum(1 for typo in typos if typo in text.lower())
        if typo_count > 0:
            issues.append(f"Possible typos detected ({typo_count})")
            risk_level = "medium"
        
        return {
            "tool": "grammar_check",
            "risk_level": risk_level,
            "issues": issues,
            "all_caps_words": all_caps_words,
            "typo_count": typo_count
        }


def create_tools():
    """Create tool functions for LangChain agent"""
    tools_instance = PhishingTools()
    
    return {
        "domain_check": tools_instance.check_domain_reputation,
        "url_check": tools_instance.check_urls,
        "urgency_analysis": tools_instance.analyze_urgency_indicators,
        "spoofing_check": tools_instance.check_sender_spoofing,
        "grammar_check": tools_instance.detect_grammar_quality,
    }
