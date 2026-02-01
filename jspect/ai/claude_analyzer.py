"""
Claude AI analyzer for JSpect.
Uses Anthropic's Claude API for intelligent secret analysis.
"""

import json
import os
from typing import Dict, List, Optional
from anthropic import Anthropic


class ClaudeAnalyzer:
    """Analyzer using Claude AI for secret validation and analysis."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Claude analyzer.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable.")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.max_tokens = 4096
    
    def analyze_secret(self, secret: Dict, code_context: str) -> Dict:
        """
        Analyze a detected secret using Claude AI.
        
        Args:
            secret: Secret detection result from regex patterns
            code_context: Surrounding code context
            
        Returns:
            Enhanced secret information with AI analysis
        """
        prompt = self._build_analysis_prompt(secret, code_context)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse Claude's response
            analysis = self._parse_response(response.content[0].text)
            
            # Enhance the original secret with AI analysis
            enhanced = {
                **secret,
                'ai_analysis': analysis,
                'severity': analysis.get('severity', 'Unknown'),
                'confidence_score': analysis.get('confidence', 0),
                'is_real_secret': analysis.get('is_real_secret', True),
                'remediation': analysis.get('remediation', ''),
                'ai_provider': 'claude'
            }
            
            return enhanced
        
        except Exception as e:
            # Return original secret with error information
            return {
                **secret,
                'ai_analysis': {'error': str(e)},
                'ai_provider': 'claude',
                'ai_error': True
            }
    
    def analyze_batch(self, secrets: List[Dict], code_context: str) -> List[Dict]:
        """
        Analyze multiple secrets in batch.
        
        Args:
            secrets: List of detected secrets
            code_context: Code context
            
        Returns:
            List of enhanced secrets
        """
        results = []
        for secret in secrets:
            enhanced = self.analyze_secret(secret, code_context)
            results.append(enhanced)
        
        return results
    
    def _build_analysis_prompt(self, secret: Dict, code_context: str) -> str:
        """
        Build prompt for Claude analysis.
        
        Args:
            secret: Secret detection result
            code_context: Code context
            
        Returns:
            Prompt string
        """
        prompt = f"""Analyze this JavaScript code snippet for security issues:

Code Context:
```javascript
{code_context}
```

Potential Secret Detected:
- Type: {secret.get('type', 'unknown')}
- Description: {secret.get('description', 'N/A')}
- Value: {secret.get('value', 'N/A')[:50]}...
- Line: {secret.get('line_number', 'N/A')}

Tasks:
1. Determine if this is a REAL secret or a FALSE POSITIVE (test data, placeholder, example, etc.)
2. Assess severity: Critical, High, Medium, or Low
3. Identify the specific type of credential
4. Provide remediation recommendations
5. Assign a confidence score (0-100)

Consider:
- Is this a hardcoded production secret or just test/example data?
- Are there indicators this is fake (e.g., "example", "test", "dummy", "xxx", "123")?
- Does the context suggest this is actively used or just documentation?
- Is the format valid for the detected secret type?

Respond in JSON format:
{{
    "is_real_secret": true/false,
    "severity": "Critical|High|Medium|Low",
    "confidence": 0-100,
    "credential_type": "specific type",
    "reasoning": "explanation",
    "remediation": "specific steps to fix"
}}"""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict:
        """
        Parse Claude's response into structured format.
        
        Args:
            response_text: Raw response from Claude
            
        Returns:
            Parsed analysis dictionary
        """
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            
            # Fallback: parse manually
            return {
                'is_real_secret': True,
                'severity': 'Medium',
                'confidence': 50,
                'credential_type': 'Unknown',
                'reasoning': response_text,
                'remediation': 'Review and rotate if necessary'
            }
        
        except json.JSONDecodeError:
            return {
                'is_real_secret': True,
                'severity': 'Medium',
                'confidence': 50,
                'credential_type': 'Unknown',
                'reasoning': 'Failed to parse AI response',
                'remediation': 'Manual review required'
            }
    
    def test_connection(self) -> bool:
        """
        Test connection to Claude API.
        
        Returns:
            True if connection successful
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": "Say 'connection successful' if you can read this."
                    }
                ]
            )
            return True
        except Exception as e:
            print(f"Claude connection test failed: {e}")
            return False
