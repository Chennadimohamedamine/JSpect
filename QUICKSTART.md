# JSpect Quick Start Guide

Get up and running with JSpect in 5 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/Chennadimohamedamine/JSpect.git
cd JSpect

# Install dependencies
pip install -r requirements.txt

# Install JSpect
pip install -e .
```

## Setup API Keys (Optional but Recommended)

JSpect works without AI, but AI analysis significantly reduces false positives.

### Option 1: Environment Variables

```bash
export ANTHROPIC_API_KEY=your_anthropic_key
export GOOGLE_API_KEY=your_google_key
```

### Option 2: .env File

```bash
# Copy example file
cp .env.example .env

# Edit .env and add your keys
nano .env
```

Get API keys:
- Claude: https://console.anthropic.com/
- Gemini: https://makersuite.google.com/app/apikey

## Your First Scan

### Scan a URL

```bash
jspect scan https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js
```

### Scan a Local File

Create `test.js`:
```javascript
const apiKey = "[REDACTED]";
const awsKey = "AKIAIOSFODNN7EXAMPLE";
```

Then scan:
```bash
jspect scan -f test.js
```

### Scan with AI

```bash
jspect scan -f test.js --ai claude
```

## Common Commands

```bash
# Scan with AI and save results
jspect scan https://example.com/app.js --ai claude --format json -o results.json

# Filter by severity
jspect scan https://example.com/app.js --severity critical,high

# Test AI connections
jspect test

# Get help
jspect --help
jspect scan --help
```

## Output Examples

### CLI Output (Default)
Beautiful, color-coded terminal output with masked secrets

### JSON Output
```bash
jspect scan -f test.js --format json
```

### HTML Report
```bash
jspect scan -f test.js --format html -o report.html
```

## Next Steps

- Read the full [README](README.md) for detailed documentation
- Check [USAGE.md](USAGE.md) for more examples
- Learn about [Contributing](CONTRIBUTING.md)

## Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
pip install -e .
```

### "API key not provided" error
```bash
# Set your API keys
export ANTHROPIC_API_KEY=your_key
export GOOGLE_API_KEY=your_key
```

### Connection timeout
Edit `config.yaml` and increase timeout:
```yaml
scanning:
  timeout: 60
```

## Tips

1. **Start without AI** to see how pattern matching works
2. **Use AI for production scans** to reduce false positives
3. **Save important results** in JSON format for later analysis
4. **Filter by severity** to focus on critical findings
5. **Test your setup** with `jspect test`

Happy scanning! 🔍
