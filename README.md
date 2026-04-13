# JSpect - AI-Powered JavaScript Secret Scanner

> **A comprehensive Python-based tool for analyzing JavaScript files to extract sensitive information (API keys, tokens, secrets, credentials) with AI-powered analysis using Claude and Gemini.**

##  Features

- **Fast JavaScript Analysis** - Scan from URLs, files, or direct code input
- **AI-Powered Detection** - Uses Claude and Gemini for intelligent secret validation
- **Pattern Recognition** - Detects 50+ types of secrets and credentials
- **Deobfuscation** - Automatically decodes Base64, hex, and URL-encoded secrets
- **Multiple Output Formats** - CLI, JSON, HTML, Markdown, and CSV
- **Batch Processing** - Scan multiple URLs concurrently
-  **Beautiful CLI** - Color-coded results with rich formatting
- **Security First** - Never logs actual secret values

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/Chennadimohamedamine/JSpect.git
cd JSpect

# Install dependencies
pip install -r requirements.txt

# Install JSpect
pip install -e .
```

### Via pip (coming soon)

```bash
pip install jspect
```

## Configuration

### 1. Set up API Keys

JSpect uses AI providers for intelligent analysis. You'll need at least one API key:

#### Claude (Anthropic)
1. Get your API key from [Anthropic Console](https://console.anthropic.com/)
2. Set environment variable: `export ANTHROPIC_API_KEY=your_key_here`

#### Gemini (Google)
1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set environment variable: `export GOOGLE_API_KEY=your_key_here`

### 2. Create .env file

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Configure settings (optional)

Edit `config.yaml` to customize:
- AI models and providers
- Detection sensitivity
- Output formats
- Scanning timeouts

## Usage

### Basic Scanning

```bash
# Scan a JavaScript file from URL
jspect scan https://example.com/app.js

# Scan a local file
jspect scan -f path/to/script.js

# Scan direct code
jspect scan --code "const apiKey = 'sk-1234567890'"
```

### AI-Powered Analysis

```bash
# Use Claude for analysis
jspect scan https://example.com/app.js --ai claude

# Use Gemini for analysis
jspect scan https://example.com/app.js --ai gemini

# Use both for consensus
jspect scan https://example.com/app.js --ai both
```

### Output Formats

```bash
# JSON output
jspect scan https://example.com/app.js --format json -o results.json

# HTML report
jspect scan https://example.com/app.js --format html -o report.html

# Markdown documentation
jspect scan https://example.com/app.js --format markdown -o findings.md

# CSV for spreadsheets
jspect scan https://example.com/app.js --format csv -o data.csv
```

### Filtering

```bash
# Show only critical and high severity findings
jspect scan https://example.com/app.js --severity critical,high

# Filter by secret type
jspect scan https://example.com/app.js --type aws,github,stripe
```

### Batch Processing

Create a file with URLs (one per line):

```text
# urls.txt
https://example.com/app.js
https://example.com/vendor.js
https://cdn.example.com/bundle.js
```

Then scan all URLs:

```bash
jspect scan -f urls.txt --ai claude
```

## Detected Secret Types

JSpect can detect 50+ types of secrets including:

### Cloud Providers
- AWS Access Keys & Secret Keys
- Google Cloud API Keys
- Azure Storage Keys
- Heroku API Keys

### Services
- GitHub Tokens (Personal, OAuth, App)
- Stripe Keys (Live, Test)
- Slack Tokens & Webhooks
- SendGrid API Keys
- Twilio API Keys
- Mailgun Keys

### Credentials
- JWT Tokens
- OAuth Tokens
- Bearer Tokens
- Basic Auth
- Passwords and API Keys

### Databases
- MongoDB Connection Strings
- PostgreSQL URLs
- MySQL Connection Strings
- Redis URLs

### Encryption
- Private Keys (RSA, SSH, PGP)
- Certificates

## Example Output

```
JSpect - JavaScript Secret Scanner
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Scanning: https://example.com/app.js
AI Analysis: Claude

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL - 2 finding(s)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type:         AWS Access Key ID
Value:        AKIA****************XXXX
Location:     Line 42
Context:      const awsKey = "AKIAIOSFODNN7EXAMPLE";
Confidence:   98% (AI Verified)
Remediation:  Rotate immediately, use AWS IAM roles or AWS Secrets Manager

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical: 2 | High: 5 | Medium: 3 | Low: 1
Total Secrets Found: 11
AI Analysis: claude
```


## Configuration

### config.yaml

```yaml
ai:
  providers:
    claude:
      enabled: true
      model: claude-3-5-sonnet-20241022
      max_tokens: 4096
    gemini:
      enabled: true
      model: gemini-2.0-flash-exp
  
detectors:
  sensitivity: medium  # low, medium, high
  custom_patterns: []
  
output:
  format: cli
  mask_secrets: true
  show_context: true
  
scanning:
  timeout: 30
  max_file_size: 10485760  # 10MB
  follow_redirects: true
```
## Best Practices

### For Security Researchers

1. **Always use AI analysis** - Reduces false positives significantly
2. **Start with critical/high** - Focus on severe findings first
3. **Export results** - Keep records in JSON/HTML format
4. **Verify findings** - AI is helpful but not perfect
5. **Check context** - Consider whether secrets are actually in use

### For Developers

1. **Scan before commit** - Catch secrets before they reach production
2. **Use .env files** - Keep secrets out of code
3. **Rotate exposed secrets** - If found, rotate immediately
4. **Use secret managers** - AWS Secrets Manager, HashiCorp Vault, etc.
5. **Regular audits** - Scan periodically even after initial cleanup

## Security & Privacy

- ❌ Never logs actual secret values
- ✅ API keys stored only in environment variables
- ✅ Local processing before AI analysis
- ✅ Configurable masking of sensitive data
- ✅ No data sent to third parties except AI providers
- ✅ AI responses are not stored by providers (as per their policies)

##  Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Disclaimer

This tool is for educational and authorized security testing purposes only. Always obtain proper authorization before scanning systems you don't own. The authors are not responsible for misuse of this tool.

##  Roadmap

- [ ] Add support for more AI providers (OpenAI GPT-4, etc.)
- [ ] Implement Git repository scanning
- [ ] Add diff mode for comparing file versions
- [ ] Create web interface
- [ ] Support for more output formats (PDF, SARIF)
- [ ] Integration with popular security tools
- [ ] Custom pattern management UI
- [ ] Real-time monitoring mode
