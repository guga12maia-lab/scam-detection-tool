import re
from email.parser import Parser
from utils.validators import extract_urls, extract_emails

class EmailAnalyzer:
    def __init__(self, raw_email_text):
        self.raw_text = raw_email_text
        self.parsed = self._parse_email()
    
    def _parse_email(self):
        """Parse email from raw text"""
        # Try proper email parsing first
        parser = Parser()
        try:
            msg = parser.parsestr(self.raw_text)
            payload = msg.get_payload()
            body = payload if isinstance(payload, str) else str(payload)
            return {
                'from': msg.get('From', ''),
                'to': msg.get('To', ''),
                'subject': msg.get('Subject', ''),
                'body': body,
                'headers': dict(msg.items())
            }
        except:
            pass
        
        # Fallback: manual parsing
        lines = self.raw_text.split('\n')
        result = {
            'from': '',
            'to': '',
            'subject': '',
            'body': self.raw_text,
            'headers': {}
        }
        
        # Extract headers manually
        body_start = 0
        for i, line in enumerate(lines):
            if line.startswith('From:'):
                result['from'] = line.replace('From:', '').strip()
            elif line.startswith('To:'):
                result['to'] = line.replace('To:', '').strip()
            elif line.startswith('Subject:'):
                result['subject'] = line.replace('Subject:', '').strip()
            elif line.strip() == '' and i > 0:
                # Empty line marks end of headers
                body_start = i + 1
                result['body'] = '\n'.join(lines[body_start:])
                break
        
        return result
    
    def get_sender_domain(self):
        """Extract domain from sender email"""
        from_addr = self.parsed['from']
        if not from_addr:
            return None
        match = re.search(r'[\w.-]+@([\w.-]+)', from_addr)
        return match.group(1) if match else None
    
    def get_urls(self):
        """Extract all URLs from email body"""
        return extract_urls(self.parsed['body'])
    
    def get_mentioned_emails(self):
        """Extract email addresses from body"""
        return extract_emails(self.parsed['body'])
    
    def get_summary(self):
        """Get email summary for analysis"""
        sender_domain = self.get_sender_domain()
        return {
            'from': self.parsed['from'],
            'to': self.parsed['to'],
            'subject': self.parsed['subject'],
            'body_preview': self.parsed['body'][:500],
            'full_body': self.parsed['body'],
            'urls': self.get_urls(),
            'mentioned_emails': self.get_mentioned_emails(),
            'sender_domain': sender_domain if sender_domain else 'unknown'
        }
