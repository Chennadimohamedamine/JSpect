# Changelog

All notable changes to JSpect will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-02-01

### Added
- Initial release of JSpect
- JavaScript secret scanning from URLs, files, and direct code
- AI-powered analysis using Claude and Gemini
- 50+ secret detection patterns including:
  - AWS, Google Cloud, Azure credentials
  - GitHub, Slack, Stripe tokens
  - Database connection strings
  - JWT tokens and OAuth credentials
  - Private keys and certificates
- Multiple output formats: CLI, JSON, HTML, Markdown, CSV
- Beautiful CLI interface with Rich formatting
- Configurable scanning parameters via config.yaml
- Batch processing support for multiple URLs
- Secret masking for secure display
- Deobfuscation for Base64, hex, and URL-encoded secrets
- AI-powered false positive reduction
- Severity scoring (Critical, High, Medium, Low)
- Remediation recommendations
- Caching for AI analysis results
- Filtering by severity and secret type

### Documentation
- Comprehensive README with examples
- Quick start guide (QUICKSTART.md)
- Detailed usage examples (USAGE.md)
- Contributing guidelines (CONTRIBUTING.md)
- MIT License

### Configuration
- .env.example for API key setup
- config.yaml for customization
- .gitignore for clean repository

## [Unreleased]

### Planned Features
- OpenAI GPT-4 integration
- Git repository scanning
- Diff mode for version comparison
- Web interface
- PDF and SARIF output formats
- Integration with security tools
- Real-time monitoring mode
- Custom pattern management UI

---

For more details, see [GitHub Releases](https://github.com/Chennadimohamedamine/JSpect/releases).
