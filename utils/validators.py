import re
from email_validator import validate_email, EmailNotValidError

def validate_email_address(email):
    """Validate email address format"""
    try:
        valid = validate_email(email)
        return valid.email, True
    except EmailNotValidError:
        return email, False

def extract_urls(text):
    """Extract URLs from text"""
    url_pattern = r'https?://[^\s]+'
    return re.findall(url_pattern, text)

def extract_emails(text):
    """Extract email addresses from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)

def is_valid_domain(domain):
    """Basic domain validation"""
    domain_pattern = r'^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$'
    return re.match(domain_pattern, domain.lower()) is not None
