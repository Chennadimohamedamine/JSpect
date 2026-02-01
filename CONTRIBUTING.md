# Contributing to JSpect

Thank you for your interest in contributing to JSpect! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version)
- Relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:
- Clear description of the enhancement
- Use case and benefits
- Example implementation (if applicable)

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write or update tests as needed
5. Update documentation
6. Commit with clear messages (`git commit -m 'Add amazing feature'`)
7. Push to your fork (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip
- git

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/JSpect.git
cd JSpect

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest black flake8 mypy
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=jspect

# Run specific test
pytest tests/test_patterns.py
```

### Code Style

We use:
- **Black** for code formatting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black jspect/

# Check linting
flake8 jspect/

# Type checking
mypy jspect/
```

## Project Structure

```
JSpect/
├── jspect/
│   ├── __init__.py
│   ├── cli.py              # CLI interface
│   ├── core/
│   │   ├── __init__.py
│   │   └── scanner.py      # JavaScript scanning engine
│   ├── detectors/
│   │   ├── __init__.py
│   │   └── patterns.py     # Secret detection patterns
│   └── ai/
│       ├── __init__.py
│       ├── claude_analyzer.py
│       ├── gemini_analyzer.py
│       └── manager.py      # AI provider management
├── tests/                  # Test files
├── docs/                   # Documentation
├── config.yaml             # Configuration
├── requirements.txt
├── setup.py
└── README.md
```

## Adding New Features

### Adding a New Secret Pattern

Edit `jspect/detectors/patterns.py`:

```python
def _build_patterns(self):
    patterns = {
        # ... existing patterns ...
        'new_service': [
            (re.compile(r'pattern_regex'), 'Description'),
        ],
    }
    return patterns
```

### Adding a New AI Provider

1. Create `jspect/ai/newprovider_analyzer.py`
2. Implement the analyzer class following the existing pattern
3. Update `jspect/ai/manager.py` to include the new provider
4. Update `config.yaml` with provider configuration

### Adding a New Output Format

Edit `jspect/cli.py` and add a new method:

```python
def _output_newformat(self, findings, output_file):
    # Implementation
    pass
```

## Testing Guidelines

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies (API calls, network requests)

Example test:

```python
import pytest
from jspect.detectors.patterns import SecretPatterns

def test_detect_aws_key():
    patterns = SecretPatterns()
    code = 'const key = "AKIAIOSFODNN7EXAMPLE";'
    findings = patterns.detect_secrets(code)
    
    assert len(findings) > 0
    assert findings[0]['type'] == 'aws'
```

### Test Coverage

Aim for:
- 80%+ overall coverage
- 100% coverage for critical paths
- All new features must include tests

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def analyze_secret(self, secret: Dict, context: str) -> Dict:
    """
    Analyze a detected secret.
    
    Args:
        secret: Secret detection result
        context: Code context
        
    Returns:
        Enhanced secret with analysis
        
    Raises:
        ValueError: If secret format is invalid
    """
    pass
```

### README Updates

Update README.md when:
- Adding new features
- Changing CLI commands
- Updating dependencies
- Modifying configuration

### Comments

- Write clear, concise comments
- Explain *why*, not *what*
- Use comments sparingly (prefer self-documenting code)

## Commit Messages

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

Examples:
```
feat(detector): add support for Azure keys
fix(cli): handle empty input files correctly
docs(readme): update installation instructions
```

## Review Process

1. Automated checks must pass (if CI is configured)
2. Code review by maintainers
3. Documentation review
4. Testing verification
5. Approval and merge

## Release Process

(For maintainers)

1. Update version in `setup.py` and `__init__.py`
2. Update CHANGELOG.md
3. Create release tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. Create GitHub release
6. Publish to PyPI (if applicable)

## Getting Help

- 💬 GitHub Discussions for questions
- 🐛 GitHub Issues for bugs
- 📧 Email maintainers for security issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to JSpect! 🎉
