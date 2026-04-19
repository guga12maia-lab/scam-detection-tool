import json
from langchain_openai import ChatOpenAI
from models.email_analyzer import EmailAnalyzer
from agents.tools import PhishingTools
from utils.logger import get_logger
import config

logger = get_logger(__name__)

class PhishingDetectionAgent:
    def __init__(self):
        self.tools = PhishingTools()
        self.llm = None
        
        if not config.DEMO_MODE:
            if not config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set in environment")
            
            self.llm = ChatOpenAI(
                api_key=config.OPENAI_API_KEY,
                model=config.MODEL_NAME,
                temperature=config.TEMPERATURE,
                max_tokens=config.MAX_TOKENS
            )
    
    def analyze_email(self, raw_email: str) -> dict:
        """Analyze email for phishing indicators"""
        logger.info("Starting email analysis")
        
        # Parse email
        analyzer = EmailAnalyzer(raw_email)
        email_summary = analyzer.get_summary()
        
        # Run all analysis tools
        analysis_results = {
            "domain_check": self.tools.check_domain_reputation(email_summary['sender_domain'] or 'unknown'),
            "url_check": self.tools.check_urls(email_summary['urls']),
            "urgency_analysis": self.tools.analyze_urgency_indicators(
                email_summary['subject'] + " " + email_summary['body_preview']
            ),
            "spoofing_check": self.tools.check_sender_spoofing(
                email_summary['from'],
                email_summary['subject']
            ),
            "grammar_check": self.tools.detect_grammar_quality(
                email_summary['body_preview']
            ),
        }
        
        # In demo mode, generate detailed analysis
        if config.DEMO_MODE:
            return self._analyze_email_demo(email_summary, analysis_results)
        
        # Get LLM analysis
        llm_verdict = self._get_llm_analysis(email_summary, analysis_results)
        
        return {
            "email_summary": email_summary,
            "tool_results": analysis_results,
            "llm_analysis": llm_verdict,
            "final_verdict": self._compile_verdict(analysis_results, llm_verdict)
        }
    
    def _analyze_email_demo(self, email_summary: dict, tool_results: dict) -> dict:
        """Demo mode analysis with accurate threat detection"""
        # Analyze the actual email content for better detection
        full_body = email_summary.get('full_body', '').lower()
        subject = email_summary.get('subject', '').lower()
        sender = email_summary.get('from', '').lower()
        
        # Phishing patterns to look for
        phishing_indicators = []
        legitimacy_score = 100
        
        # Check urgency and pressure
        urgency_words = ['urgent', 'immediately', 'verify', 'confirm', 'act now', 'expires', 
                        'suspended', 'locked', 'unauthorized', 'suspicious activity']
        urgency_count = sum(full_body.count(word) for word in urgency_words)
        if urgency_count >= 2:
            phishing_indicators.append(f"High urgency language ({urgency_count} instances)")
            legitimacy_score -= 25
        
        # Check for login/credential requests
        cred_words = ['verify account', 'confirm identity', 'enter password', 'login', 'click here',
                     'confirm details', 'update information']
        cred_count = sum(full_body.count(word) for word in cred_words)
        if cred_count >= 1:
            phishing_indicators.append(f"Credential request detected ({cred_count} instances)")
            legitimacy_score -= 30
        
        # Check for generic greetings
        generic_greetings = ['dear user', 'dear customer', 'dear sir', 'dear madam']
        if any(greeting in full_body for greeting in generic_greetings):
            phishing_indicators.append("Generic greeting detected")
            legitimacy_score -= 20
        
        # Check for suspicious domains
        if 'paypa1' in sender or 'amaz0n' in sender or 'go0gle' in sender:
            phishing_indicators.append("Lookalike domain detected")
            legitimacy_score -= 40
        
        # URL shorteners are suspicious
        if 'bit.ly' in full_body or 'tinyurl' in full_body.lower():
            phishing_indicators.append("URL shortener detected")
            legitimacy_score -= 20
        
        # Check sender domain reputation
        if 'unresolvable' in str(tool_results.get('domain_check', {})).lower():
            if sender and '@' in sender:  # Only penalize if actually has sender info
                phishing_indicators.append("Sender domain cannot be verified")
                legitimacy_score -= 15
        
        # Determine threat level based on legitimacy score
        if legitimacy_score >= 85:
            threat_level = "🟢 LOW"
            confidence = 90
            recommendation = "✅ This email appears safe, but stay vigilant."
        elif legitimacy_score >= 70:
            threat_level = "🟡 MEDIUM"
            confidence = 75
            recommendation = "⚠️ Exercise caution before interacting. Report suspicious activity."
        elif legitimacy_score >= 50:
            threat_level = "🔴 HIGH"
            confidence = 85
            recommendation = "❌ DO NOT click any links or download attachments. Report to security team."
        else:
            threat_level = "🔴 CRITICAL"
            confidence = 95
            recommendation = "🚨 CLEAR PHISHING DETECTED. DO NOT INTERACT. Report immediately."
        
        # Build report
        indicators_text = "\n".join(f"  • {ind}" for ind in phishing_indicators) if phishing_indicators else "  • No major phishing indicators detected"
        
        llm_analysis = f"""
PHISHING ANALYSIS SUMMARY (Demo Mode):

Analyzed using {len(tool_results)} security tools + advanced content pattern detection.

PHISHING INDICATORS FOUND:
{indicators_text}

EMAIL DETAILS:
• From: {email_summary['from'] if email_summary['from'] else '(Not specified)'}
• Subject: {email_summary['subject'] if email_summary['subject'] else '(Not specified)'}
• URLs Found: {len(email_summary['urls'])}
• Urgency Level: {'High' if urgency_count >= 2 else 'Moderate' if urgency_count == 1 else 'Low'}

SECURITY ASSESSMENT:
{'This email shows CLEAR signs of phishing. Multiple red flags detected.' if legitimacy_score <= 50 else 'This email appears MOSTLY LEGITIMATE with only minor concerns.' if legitimacy_score >= 85 else 'This email has SOME SUSPICIOUS elements. Use caution.'}

RECOMMENDATION:
{recommendation}

[Running in DEMO MODE - No API calls made]
"""
        
        return {
            "email_summary": email_summary,
            "tool_results": tool_results,
            "llm_analysis": llm_analysis,
            "final_verdict": {
                "threat_level": threat_level,
                "confidence_score": confidence,
                "recommendation": recommendation,
                "summary": llm_analysis
            }
        }
    
    def _get_llm_analysis(self, email_summary: dict, tool_results: dict) -> str:
        """Get LLM analysis and reasoning"""
        prompt = f"""
Analyze this email for phishing indicators. Consider the following information:

EMAIL DETAILS:
- From: {email_summary['from']}
- To: {email_summary['to']}
- Subject: {email_summary['subject']}
- Body Preview: {email_summary['body_preview'][:300]}

TOOL ANALYSIS RESULTS:
{json.dumps(tool_results, indent=2)}

Based on the analysis:
1. Summarize the key phishing indicators found
2. Assess the overall threat level (Low/Medium/High/Critical)
3. Provide specific recommendations
4. Explain your reasoning clearly

Be concise and direct in your assessment.
"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}")
            return "Analysis unavailable - API error"
    
    def _compile_verdict(self, tool_results: dict, llm_analysis: str) -> dict:
        """Compile final verdict from all analysis"""
        # Calculate risk score from tools
        high_risk_indicators = 0
        medium_risk_indicators = 0
        
        for tool_name, result in tool_results.items():
            if isinstance(result, dict):
                risk = result.get("risk_level", "low")
                if risk == "high":
                    high_risk_indicators += 1
                elif risk == "medium":
                    medium_risk_indicators += 1
        
        # Determine threat level
        if high_risk_indicators >= 3:
            threat_level = "🔴 CRITICAL"
            confidence = 95
        elif high_risk_indicators >= 2:
            threat_level = "🔴 HIGH"
            confidence = 85
        elif high_risk_indicators >= 1 or medium_risk_indicators >= 3:
            threat_level = "🟡 MEDIUM"
            confidence = 70
        else:
            threat_level = "🟢 LOW"
            confidence = 90
        
        return {
            "threat_level": threat_level,
            "confidence_score": confidence,
            "recommendation": "Do not click links or download attachments" if "CRITICAL" in threat_level or "HIGH" in threat_level else "Proceed with caution",
            "summary": llm_analysis
        }
