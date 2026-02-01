"""
Secret detection patterns for JSpect.
Implements regex patterns for detecting various types of secrets in JavaScript code.
"""

import re
from typing import Dict, List, Tuple, Pattern

class SecretPatterns:
    """Collection of regex patterns for detecting secrets."""
    
    def __init__(self):
        """Initialize secret patterns."""
        self.patterns = self._build_patterns()
    
    def _build_patterns(self) -> Dict[str, List[Tuple[Pattern, str]]]:
        """
        Build and compile all secret detection patterns.
        
        Returns:
            Dictionary mapping secret types to list of (pattern, description) tuples
        """
        patterns = {
            'aws': [
                (re.compile(r'AKIA[0-9A-Z]{16}'), 'AWS Access Key ID'),
                (re.compile(r'(?i)aws(.{0,20})?[\'"][0-9a-zA-Z\/+]{40}[\'"]'), 'AWS Secret Access Key'),
            ],
            'google': [
                (re.compile(r'AIza[0-9A-Za-z\-_]{35}'), 'Google API Key'),
                (re.compile(r'ya29\.[0-9A-Za-z\-_]+'), 'Google OAuth Access Token'),
            ],
            'stripe': [
                (re.compile(r'sk_live_[0-9a-zA-Z]{24,}'), 'Stripe Live Secret Key'),
                (re.compile(r'rk_live_[0-9a-zA-Z]{24,}'), 'Stripe Live Restricted Key'),
                (re.compile(r'pk_live_[0-9a-zA-Z]{24,}'), 'Stripe Live Public Key'),
            ],
            'github': [
                (re.compile(r'ghp_[0-9a-zA-Z]{36}'), 'GitHub Personal Access Token'),
                (re.compile(r'gho_[0-9a-zA-Z]{36}'), 'GitHub OAuth Access Token'),
                (re.compile(r'ghs_[0-9a-zA-Z]{36}'), 'GitHub App Token'),
                (re.compile(r'github_pat_[0-9a-zA-Z_]{82}'), 'GitHub Fine-grained Personal Access Token'),
            ],
            'slack': [
                (re.compile(r'xox[baprs]-[0-9]{10,12}-[0-9]{10,12}-[0-9a-zA-Z]{24,}'), 'Slack Token'),
                (re.compile(r'https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+'), 'Slack Webhook'),
            ],
            'twitter': [
                (re.compile(r'(?i)twitter(.{0,20})?[\'"][0-9a-z]{35,44}[\'"]'), 'Twitter Secret Key'),
            ],
            'facebook': [
                (re.compile(r'(?i)facebook(.{0,20})?[\'"][0-9a-f]{32}[\'"]'), 'Facebook Access Token'),
            ],
            'twilio': [
                (re.compile(r'SK[0-9a-fA-F]{32}'), 'Twilio API Key'),
            ],
            'sendgrid': [
                (re.compile(r'SG\.[0-9A-Za-z\-_]{22}\.[0-9A-Za-z\-_]{43}'), 'SendGrid API Key'),
            ],
            'mailgun': [
                (re.compile(r'key-[0-9a-zA-Z]{32}'), 'Mailgun API Key'),
            ],
            'jwt': [
                (re.compile(r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*'), 'JSON Web Token'),
            ],
            'bearer': [
                (re.compile(r'(?i)bearer\s+[a-zA-Z0-9\-_.~+/]+'), 'Bearer Token'),
            ],
            'basic_auth': [
                (re.compile(r'(?i)basic\s+[a-zA-Z0-9+/=]+'), 'Basic Auth Credentials'),
            ],
            'private_key': [
                (re.compile(r'-----BEGIN (?:RSA |OPENSSH |DSA |EC |PGP )?PRIVATE KEY-----'), 'Private Key'),
                (re.compile(r'-----BEGIN CERTIFICATE-----'), 'Certificate'),
            ],
            'azure': [
                (re.compile(r'(?i)DefaultEndpointsProtocol=https;AccountName=[a-z0-9]+;AccountKey=[a-zA-Z0-9+/=]{88}'), 'Azure Storage Account Key'),
            ],
            'heroku': [
                (re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'), 'Heroku API Key'),
            ],
            'mongodb': [
                (re.compile(r'mongodb(\+srv)?://[^\s]+'), 'MongoDB Connection String'),
            ],
            'postgresql': [
                (re.compile(r'postgres(ql)?://[^\s]+'), 'PostgreSQL Connection String'),
            ],
            'mysql': [
                (re.compile(r'mysql://[^\s]+'), 'MySQL Connection String'),
            ],
            'redis': [
                (re.compile(r'redis://[^\s]+'), 'Redis Connection String'),
            ],
            'credentials': [
                (re.compile(r'(?i)(?:password|passwd|pwd)[\s]*[=:]+[\s]*[\'"]([^\'"]+)[\'"]'), 'Password'),
                (re.compile(r'(?i)(?:api[_-]?key|apikey)[\s]*[=:]+[\s]*[\'"]([^\'"]+)[\'"]'), 'API Key'),
                (re.compile(r'(?i)(?:secret|token)[\s]*[=:]+[\s]*[\'"]([^\'"]+)[\'"]'), 'Secret/Token'),
            ],
            'generic_secrets': [
                (re.compile(r'[\'"]([a-zA-Z0-9_-]{32,})[\'"]'), 'Potential Secret (Long String)'),
            ],
        }
        
        return patterns
    
    def get_all_patterns(self) -> Dict[str, List[Tuple[Pattern, str]]]:
        """
        Get all patterns.
        
        Returns:
            Dictionary of all patterns
        """
        return self.patterns
    
    def get_patterns_by_type(self, secret_type: str) -> List[Tuple[Pattern, str]]:
        """
        Get patterns for a specific secret type.
        
        Args:
            secret_type: Type of secret (e.g., 'aws', 'github')
            
        Returns:
            List of (pattern, description) tuples
        """
        return self.patterns.get(secret_type, [])
    
    def detect_secrets(self, content: str) -> List[Dict[str, any]]:
        """
        Detect secrets in the given content.
        
        Args:
            content: JavaScript code content to scan
            
        Returns:
            List of detected secrets with metadata
        """
        findings = []
        lines = content.split('\n')
        
        for secret_type, pattern_list in self.patterns.items():
            for pattern, description in pattern_list:
                for line_num, line in enumerate(lines, 1):
                    matches = pattern.finditer(line)
                    for match in matches:
                        # Get surrounding context
                        start_line = max(0, line_num - 3)
                        end_line = min(len(lines), line_num + 2)
                        context = '\n'.join(lines[start_line:end_line])
                        
                        findings.append({
                            'type': secret_type,
                            'description': description,
                            'value': match.group(0),
                            'line_number': line_num,
                            'line_content': line.strip(),
                            'context': context,
                            'confidence': 'regex',  # Will be updated by AI
                        })
        
        return findings
    
    def mask_secret(self, secret: str, show_chars: int = 4) -> str:
        """
        Mask a secret value for display.
        
        Args:
            secret: The secret value to mask
            show_chars: Number of characters to show at start and end
            
        Returns:
            Masked secret string
        """
        if len(secret) <= show_chars * 2:
            return '*' * len(secret)
        
        start = secret[:show_chars]
        end = secret[-show_chars:]
        masked_length = len(secret) - (show_chars * 2)
        
        return f"{start}{'*' * masked_length}{end}"
