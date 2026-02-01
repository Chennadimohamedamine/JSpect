"""
JavaScript analysis engine for JSpect.
Handles fetching, parsing, and analyzing JavaScript code.
"""

import re
import base64
import urllib.parse
from typing import Dict, List, Optional, Union
import requests
from bs4 import BeautifulSoup
import yaml
import os


class JavaScriptScanner:
    """Scanner for JavaScript code analysis."""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize the JavaScript scanner.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.timeout = self.config.get('scanning', {}).get('timeout', 30)
        self.max_file_size = self.config.get('scanning', {}).get('max_file_size', 10485760)
        self.follow_redirects = self.config.get('scanning', {}).get('follow_redirects', True)
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to config file
            
        Returns:
            Configuration dictionary
        """
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            return {}
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            return {}
    
    def fetch_from_url(self, url: str) -> Optional[str]:
        """
        Fetch JavaScript content from a URL.
        
        Args:
            url: URL to fetch JavaScript from
            
        Returns:
            JavaScript content or None if failed
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=self.follow_redirects
            )
            response.raise_for_status()
            
            # Check file size
            if len(response.content) > self.max_file_size:
                raise ValueError(f"File too large: {len(response.content)} bytes")
            
            return response.text
        
        except Exception as e:
            raise Exception(f"Failed to fetch URL {url}: {str(e)}")
    
    def fetch_from_file(self, file_path: str) -> str:
        """
        Read JavaScript content from a local file.
        
        Args:
            file_path: Path to JavaScript file
            
        Returns:
            JavaScript content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if len(content) > self.max_file_size:
                raise ValueError(f"File too large: {len(content)} bytes")
            
            return content
        
        except Exception as e:
            raise Exception(f"Failed to read file {file_path}: {str(e)}")
    
    def fetch_urls_from_file(self, file_path: str) -> List[str]:
        """
        Read a list of URLs from a file.
        
        Args:
            file_path: Path to file containing URLs (one per line)
            
        Returns:
            List of URLs
        """
        try:
            with open(file_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            return urls
        
        except Exception as e:
            raise Exception(f"Failed to read URLs file {file_path}: {str(e)}")
    
    def deobfuscate(self, code: str) -> str:
        """
        Attempt to deobfuscate JavaScript code.
        
        Args:
            code: Potentially obfuscated JavaScript code
            
        Returns:
            Deobfuscated code (or original if deobfuscation fails)
        """
        modified = code
        
        # Try to decode base64 strings
        base64_pattern = re.compile(r'[\'"]([A-Za-z0-9+/]{20,}={0,2})[\'"]')
        for match in base64_pattern.finditer(code):
            try:
                decoded = base64.b64decode(match.group(1)).decode('utf-8', errors='ignore')
                if decoded.isprintable():
                    modified = modified.replace(match.group(1), f"[BASE64_DECODED: {decoded}]")
            except:
                pass
        
        # Try to decode URL-encoded strings
        url_pattern = re.compile(r'[\'"]([^\'"]*%[0-9A-Fa-f]{2}[^\'"]*)[\'"]')
        for match in url_pattern.finditer(code):
            try:
                decoded = urllib.parse.unquote(match.group(1))
                if decoded != match.group(1):
                    modified = modified.replace(match.group(1), f"[URL_DECODED: {decoded}]")
            except:
                pass
        
        # Try to decode hex strings
        hex_pattern = re.compile(r'\\x([0-9a-fA-F]{2})')
        if hex_pattern.search(code):
            try:
                modified = re.sub(
                    hex_pattern,
                    lambda m: chr(int(m.group(1), 16)),
                    modified
                )
            except:
                pass
        
        return modified
    
    def extract_strings(self, code: str) -> List[str]:
        """
        Extract all string literals from JavaScript code.
        
        Args:
            code: JavaScript code
            
        Returns:
            List of extracted strings
        """
        # Match single and double quoted strings
        string_pattern = re.compile(r'[\'"]([^\'"\\]*(\\.[^\'"\\]*)*)[\'"]')
        strings = [match.group(1) for match in string_pattern.finditer(code)]
        
        # Match template literals
        template_pattern = re.compile(r'`([^`]*)`')
        strings.extend([match.group(1) for match in template_pattern.finditer(code)])
        
        return strings
    
    def analyze_code(self, code: str, source: str = 'unknown') -> Dict:
        """
        Analyze JavaScript code structure and extract metadata.
        
        Args:
            code: JavaScript code to analyze
            source: Source identifier (URL or file path)
            
        Returns:
            Analysis results dictionary
        """
        lines = code.split('\n')
        
        analysis = {
            'source': source,
            'line_count': len(lines),
            'char_count': len(code),
            'has_obfuscation': self._detect_obfuscation(code),
            'strings': self.extract_strings(code),
            'functions': self._extract_function_names(code),
            'urls': self._extract_urls(code),
            'deobfuscated_code': self.deobfuscate(code) if self._detect_obfuscation(code) else code,
        }
        
        return analysis
    
    def _detect_obfuscation(self, code: str) -> bool:
        """
        Detect if JavaScript code appears to be obfuscated.
        
        Args:
            code: JavaScript code
            
        Returns:
            True if code appears obfuscated
        """
        # Check for common obfuscation indicators
        indicators = [
            len(re.findall(r'\\x[0-9a-fA-F]{2}', code)) > 10,  # Hex encoding
            len(re.findall(r'\\u[0-9a-fA-F]{4}', code)) > 10,  # Unicode encoding
            code.count('eval(') > 3,  # Multiple eval calls
            code.count('Function(') > 3,  # Function constructor
            len(re.findall(r'[A-Za-z0-9+/]{50,}={0,2}', code)) > 5,  # Base64 strings
        ]
        
        return sum(indicators) >= 2
    
    def _extract_function_names(self, code: str) -> List[str]:
        """
        Extract function names from JavaScript code.
        
        Args:
            code: JavaScript code
            
        Returns:
            List of function names
        """
        # Match function declarations
        func_pattern = re.compile(r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)')
        functions = func_pattern.findall(code)
        
        # Match arrow functions assigned to variables
        arrow_pattern = re.compile(r'(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*\([^)]*\)\s*=>')
        functions.extend(arrow_pattern.findall(code))
        
        return list(set(functions))
    
    def _extract_urls(self, code: str) -> List[str]:
        """
        Extract URLs from JavaScript code.
        
        Args:
            code: JavaScript code
            
        Returns:
            List of URLs
        """
        url_pattern = re.compile(r'https?://[^\s\'"<>]+')
        urls = url_pattern.findall(code)
        return list(set(urls))
    
    def scan(self, source: Union[str, List[str]], source_type: str = 'url') -> List[Dict]:
        """
        Scan JavaScript source(s) for analysis.
        
        Args:
            source: URL, file path, code string, or list of URLs
            source_type: Type of source ('url', 'file', 'code', 'url_list')
            
        Returns:
            List of scan results
        """
        results = []
        
        if source_type == 'url':
            code = self.fetch_from_url(source)
            analysis = self.analyze_code(code, source)
            results.append(analysis)
        
        elif source_type == 'file':
            code = self.fetch_from_file(source)
            analysis = self.analyze_code(code, source)
            results.append(analysis)
        
        elif source_type == 'code':
            analysis = self.analyze_code(source, 'direct_input')
            results.append(analysis)
        
        elif source_type == 'url_list':
            if isinstance(source, str):
                urls = self.fetch_urls_from_file(source)
            else:
                urls = source
            
            for url in urls:
                try:
                    code = self.fetch_from_url(url)
                    analysis = self.analyze_code(code, url)
                    results.append(analysis)
                except Exception as e:
                    results.append({
                        'source': url,
                        'error': str(e),
                        'success': False
                    })
        
        return results
