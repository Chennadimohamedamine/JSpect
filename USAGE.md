# JSpect Usage Examples

This document provides practical examples of using JSpect for various scenarios.

## Table of Contents

1. [Basic Scanning](#basic-scanning)
2. [AI-Powered Analysis](#ai-powered-analysis)
3. [Output Formats](#output-formats)
4. [Filtering Results](#filtering-results)
5. [Batch Processing](#batch-processing)
6. [Bug Bounty Tips](#bug-bounty-tips)

## Basic Scanning

### Scan a Remote JavaScript File

```bash
jspect scan https://example.com/assets/app.js
```

### Scan a Local File

```bash
jspect scan -f /path/to/local/script.js
```

### Scan Direct Code

```bash
jspect scan --code "const apiKey = 'sk_test_xyz123';"
```

### Scan with Wildcards (Bash)

```bash
# Scan all JS files in a directory
for file in src/*.js; do
    jspect scan -f "$file"
done
```

## AI-Powered Analysis

### Use Claude for Analysis

```bash
# Set API key first
export ANTHROPIC_API_KEY=your_key_here

# Scan with Claude
jspect scan https://example.com/app.js --ai claude
```

### Use Gemini for Analysis

```bash
# Set API key first
export GOOGLE_API_KEY=your_key_here

# Scan with Gemini
jspect scan https://example.com/app.js --ai gemini
```

### Use Both AI Providers (Consensus)

```bash
# Both keys must be set
export ANTHROPIC_API_KEY=your_anthropic_key
export GOOGLE_API_KEY=your_google_key

# Scan with both
jspect scan https://example.com/app.js --ai both
```

## Output Formats

### JSON Output

```bash
# Print to stdout
jspect scan https://example.com/app.js --format json

# Save to file
jspect scan https://example.com/app.js --format json -o results.json
```

### HTML Report

```bash
jspect scan https://example.com/app.js --format html -o report.html
```

### Markdown Documentation

```bash
jspect scan https://example.com/app.js --format markdown -o findings.md
```

### CSV for Analysis

```bash
jspect scan https://example.com/app.js --format csv -o data.csv
```

## Filtering Results

### Filter by Severity

```bash
# Only critical findings
jspect scan https://example.com/app.js --severity critical

# Critical and high
jspect scan https://example.com/app.js --severity critical,high --ai claude

# Medium and low
jspect scan https://example.com/app.js --severity medium,low
```

### Filter by Secret Type

```bash
# Only AWS secrets
jspect scan https://example.com/app.js --type aws

# AWS and GitHub secrets
jspect scan https://example.com/app.js --type aws,github

# Multiple types with AI
jspect scan https://example.com/app.js --type aws,github,stripe --ai claude
```

### Combine Filters

```bash
# Critical AWS secrets only
jspect scan https://example.com/app.js --severity critical --type aws --ai claude
```

## Batch Processing

### Create URL List File

Create `urls.txt`:
```
https://example.com/js/app.js
https://example.com/js/vendor.js
https://cdn.example.com/bundle.js
https://static.example.com/main.js
```

### Scan All URLs

```bash
jspect scan -f urls.txt --ai claude --format json -o batch-results.json
```

### Process Results with jq

```bash
# Count findings by severity
jspect scan -f urls.txt --format json | jq '.summary.by_severity'

# Extract only critical findings
jspect scan -f urls.txt --format json | \
    jq '.findings[] | select(.severity == "Critical")'

# Get all AWS keys
jspect scan -f urls.txt --format json | \
    jq '.findings[] | select(.type == "aws")'
```

## Bug Bounty Tips

### Quick Recon

```bash
# Scan target's main JS files
jspect scan https://target.com/assets/*.js --severity critical,high --ai claude

# Save results
jspect scan https://target.com/assets/*.js --ai claude --format html -o target-scan.html
```

### Deep Analysis

```bash
# 1. Collect all JS URLs (using tools like waybackurls, gau, etc.)
cat js-urls.txt | sort -u > unique-js-urls.txt

# 2. Scan with AI for better accuracy
jspect scan -f unique-js-urls.txt --ai both --format json -o deep-scan.json

# 3. Filter critical findings
cat deep-scan.json | jq '.findings[] | select(.severity == "Critical")'
```

### Continuous Monitoring

```bash
#!/bin/bash
# monitor-target.sh

TARGET="https://target.com"
OUTPUT_DIR="./scans/$(date +%Y%m%d)"

mkdir -p "$OUTPUT_DIR"

# Scan and save results
jspect scan "$TARGET/app.js" \
    --ai claude \
    --format json \
    -o "$OUTPUT_DIR/scan-$(date +%H%M%S).json"

# Compare with previous scan
# (implement diff logic here)
```

### CI/CD Integration

```bash
#!/bin/bash
# .github/workflows/secret-scan.sh

# Scan build artifacts
jspect scan -f build/static/js/*.js --format json -o scan-results.json

# Check for critical findings
CRITICAL_COUNT=$(cat scan-results.json | jq '[.findings[] | select(.severity == "Critical")] | length')

if [ "$CRITICAL_COUNT" -gt 0 ]; then
    echo "Found $CRITICAL_COUNT critical secrets!"
    exit 1
fi

echo "No critical secrets found."
```

## Advanced Examples

### Scan with Custom Headers

```bash
# JSpect uses requests library, so you can't directly pass headers
# Instead, download first, then scan

curl -H "Authorization: Bearer token" https://example.com/app.js > app.js
jspect scan -f app.js --ai claude
```

### Pipeline Processing

```bash
# Download, scan, filter, and report
curl -s https://example.com/app.js | \
    jspect scan --code - --format json | \
    jq '.findings[] | select(.confidence_score > 80)' | \
    tee high-confidence-secrets.json
```

### Comparison Scan

```bash
# Scan current version
jspect scan https://example.com/app.js --format json -o current.json

# Scan old version
jspect scan https://example.com/old/app.js --format json -o old.json

# Compare (using jq)
jq -s '.[0].findings - .[1].findings' current.json old.json
```

## Testing AI Connections

```bash
# Test if AI providers are accessible
jspect test
```

Expected output:
```
✓ Claude: Connected
✓ Gemini: Connected
```

## Environment Variables

### Using .env File

Create `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-xxx
GOOGLE_API_KEY=AIzaXXX
```

Then run:
```bash
# JSpect automatically loads .env
jspect scan https://example.com/app.js --ai claude
```

### Using Export

```bash
export ANTHROPIC_API_KEY=sk-ant-xxx
export GOOGLE_API_KEY=AIzaXXX

jspect scan https://example.com/app.js --ai both
```

## Real-World Scenarios

### Scenario 1: Quick Bug Bounty Check

```bash
# 1. Find JS files
echo "target.com" | waybackurls | grep -E "\.js$" > js-files.txt

# 2. Scan with AI
jspect scan -f js-files.txt --ai claude --severity critical,high -o findings.json

# 3. Review results
cat findings.json | jq '.findings[] | {type, severity, value, line_number}'
```

### Scenario 2: Pre-Commit Hook

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash

# Scan staged JS files
for file in $(git diff --cached --name-only | grep -E "\.js$"); do
    echo "Scanning $file..."
    jspect scan -f "$file" --severity critical,high --format json > /tmp/scan.json
    
    FINDINGS=$(cat /tmp/scan.json | jq '.summary.total')
    if [ "$FINDINGS" -gt 0 ]; then
        echo "❌ Found secrets in $file"
        cat /tmp/scan.json | jq '.findings[]'
        exit 1
    fi
done

echo "✓ No secrets found"
```

### Scenario 3: Security Audit Report

```bash
#!/bin/bash
# audit.sh

TARGET=$1
DATE=$(date +%Y-%m-%d)
REPORT_DIR="audit-reports/$DATE"

mkdir -p "$REPORT_DIR"

# Scan with both AI providers
jspect scan "$TARGET" \
    --ai both \
    --format html \
    -o "$REPORT_DIR/full-report.html"

jspect scan "$TARGET" \
    --ai both \
    --format json \
    -o "$REPORT_DIR/data.json"

jspect scan "$TARGET" \
    --ai both \
    --format markdown \
    -o "$REPORT_DIR/summary.md"

echo "Audit report generated in $REPORT_DIR"
```

## Performance Tips

1. **Use caching**: AI results are cached for 24 hours by default
2. **Filter early**: Use `--severity` and `--type` to reduce processing
3. **Batch wisely**: Process 10-20 URLs at a time to avoid rate limits
4. **Choose format**: Use JSON for programmatic processing, CLI for quick checks

## Troubleshooting

### API Key Issues

```bash
# Check if keys are set
echo $ANTHROPIC_API_KEY
echo $GOOGLE_API_KEY

# Test connections
jspect test
```

### Timeout Issues

Edit `config.yaml`:
```yaml
scanning:
  timeout: 60  # Increase timeout
```

### Rate Limiting

If you hit rate limits:
- Add delays between scans
- Use caching (enabled by default)
- Reduce batch size

---

For more information, see the [main README](README.md).
