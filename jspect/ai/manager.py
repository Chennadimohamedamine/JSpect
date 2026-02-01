"""
AI Manager for JSpect.
Unified interface for multiple AI providers with fallback and caching.
"""

import os
import json
import hashlib
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import yaml

try:
    from .claude_analyzer import ClaudeAnalyzer
    from .gemini_analyzer import GeminiAnalyzer
except ImportError:
    from claude_analyzer import ClaudeAnalyzer
    from gemini_analyzer import GeminiAnalyzer


class AIManager:
    """Manages AI providers for secret analysis."""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize AI Manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.cache = {}
        self.cache_ttl = timedelta(hours=24)
        
        # Initialize providers
        self.providers = {}
        self._init_providers()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            return {}
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            return {}
    
    def _init_providers(self):
        """Initialize AI providers based on configuration."""
        ai_config = self.config.get('ai', {}).get('providers', {})
        
        # Initialize Claude
        claude_config = ai_config.get('claude', {})
        if claude_config.get('enabled', True):
            try:
                self.providers['claude'] = ClaudeAnalyzer(
                    model=claude_config.get('model', 'claude-3-5-sonnet-20241022')
                )
            except Exception as e:
                print(f"Warning: Could not initialize Claude: {e}")
        
        # Initialize Gemini
        gemini_config = ai_config.get('gemini', {})
        if gemini_config.get('enabled', True):
            try:
                self.providers['gemini'] = GeminiAnalyzer(
                    model=gemini_config.get('model', 'gemini-2.0-flash-exp')
                )
            except Exception as e:
                print(f"Warning: Could not initialize Gemini: {e}")
    
    def analyze_secret(
        self,
        secret: Dict,
        code_context: str,
        provider: str = 'claude',
        use_cache: bool = True
    ) -> Dict:
        """
        Analyze a secret using specified AI provider.
        
        Args:
            secret: Secret detection result
            code_context: Code context
            provider: AI provider to use ('claude', 'gemini', 'both')
            use_cache: Whether to use cached results
            
        Returns:
            Enhanced secret with AI analysis
        """
        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(secret, code_context)
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached
        
        # Analyze with specified provider(s)
        if provider == 'both':
            result = self._analyze_with_both(secret, code_context)
        else:
            result = self._analyze_with_provider(secret, code_context, provider)
        
        # Cache result
        if use_cache:
            cache_key = self._get_cache_key(secret, code_context)
            self._add_to_cache(cache_key, result)
        
        return result
    
    def analyze_batch(
        self,
        secrets: List[Dict],
        code_context: str,
        provider: str = 'claude',
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Analyze multiple secrets.
        
        Args:
            secrets: List of secrets
            code_context: Code context
            provider: AI provider to use
            use_cache: Whether to use cache
            
        Returns:
            List of enhanced secrets
        """
        results = []
        for secret in secrets:
            enhanced = self.analyze_secret(secret, code_context, provider, use_cache)
            results.append(enhanced)
        
        return results
    
    def _analyze_with_provider(
        self,
        secret: Dict,
        code_context: str,
        provider: str
    ) -> Dict:
        """Analyze with a specific provider with fallback."""
        if provider not in self.providers:
            # Try fallback
            if 'claude' in self.providers:
                provider = 'claude'
            elif 'gemini' in self.providers:
                provider = 'gemini'
            else:
                return {
                    **secret,
                    'ai_analysis': {'error': 'No AI providers available'},
                    'ai_error': True
                }
        
        try:
            analyzer = self.providers[provider]
            return analyzer.analyze_secret(secret, code_context)
        except Exception as e:
            # Try fallback to another provider
            for fallback_provider in ['claude', 'gemini']:
                if fallback_provider != provider and fallback_provider in self.providers:
                    try:
                        analyzer = self.providers[fallback_provider]
                        return analyzer.analyze_secret(secret, code_context)
                    except:
                        continue
            
            # All providers failed
            return {
                **secret,
                'ai_analysis': {'error': str(e)},
                'ai_error': True
            }
    
    def _analyze_with_both(self, secret: Dict, code_context: str) -> Dict:
        """Analyze with both providers and combine results."""
        results = []
        
        for provider in ['claude', 'gemini']:
            if provider in self.providers:
                try:
                    result = self.providers[provider].analyze_secret(secret, code_context)
                    results.append(result)
                except:
                    continue
        
        if not results:
            return {
                **secret,
                'ai_analysis': {'error': 'All providers failed'},
                'ai_error': True
            }
        
        # Combine results with consensus
        return self._combine_analyses(secret, results)
    
    def _combine_analyses(self, secret: Dict, results: List[Dict]) -> Dict:
        """Combine multiple AI analyses into consensus."""
        if not results:
            return secret
        
        if len(results) == 1:
            return results[0]
        
        # Calculate consensus
        is_real_count = sum(1 for r in results if r.get('is_real_secret', True))
        avg_confidence = sum(r.get('confidence_score', 50) for r in results) / len(results)
        
        # Get most severe severity
        severity_order = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
        severities = [r.get('severity', 'Medium') for r in results]
        max_severity = max(severities, key=lambda s: severity_order.get(s, 2))
        
        # Combine remediations
        remediations = [r.get('remediation', '') for r in results if r.get('remediation')]
        combined_remediation = ' | '.join(set(remediations))
        
        return {
            **secret,
            'ai_analysis': {
                'is_real_secret': is_real_count > len(results) / 2,
                'severity': max_severity,
                'confidence': int(avg_confidence),
                'combined_from': [r.get('ai_provider', 'unknown') for r in results],
                'reasoning': 'Consensus from multiple AI providers'
            },
            'severity': max_severity,
            'confidence_score': int(avg_confidence),
            'is_real_secret': is_real_count > len(results) / 2,
            'remediation': combined_remediation,
            'ai_provider': 'combined'
        }
    
    def _get_cache_key(self, secret: Dict, code_context: str) -> str:
        """Generate cache key for a secret analysis."""
        key_data = f"{secret.get('value', '')}{code_context}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get result from cache if not expired."""
        if key in self.cache:
            cached_time, result = self.cache[key]
            if datetime.now() - cached_time < self.cache_ttl:
                return result
            else:
                del self.cache[key]
        return None
    
    def _add_to_cache(self, key: str, result: Dict):
        """Add result to cache."""
        self.cache[key] = (datetime.now(), result)
    
    def clear_cache(self):
        """Clear the analysis cache."""
        self.cache.clear()
    
    def test_providers(self) -> Dict[str, bool]:
        """
        Test all configured providers.
        
        Returns:
            Dictionary mapping provider names to their status
        """
        status = {}
        for name, provider in self.providers.items():
            try:
                status[name] = provider.test_connection()
            except:
                status[name] = False
        
        return status
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available providers.
        
        Returns:
            List of provider names
        """
        return list(self.providers.keys())
