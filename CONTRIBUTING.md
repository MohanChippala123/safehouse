# Contributing to SafeHouse

Thank you for your interest in contributing to SafeHouse! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork>`
3. Create a branch: `git checkout -b feature/your-feature`
4. Set up development environment: `python setup.py`
5. Make your changes
6. Test thoroughly
7. Commit with clear messages
8. Push to your fork
9. Open a pull request

## Development Setup

```bash
python setup.py
source venv/bin/activate  # or venv\Scripts\activate on Windows
cp .env.example .env
# Add your API keys to .env
python app.py
```

## Running Tests

```bash
pytest tests/
pytest tests/ --cov=.  # With coverage
pytest tests/ -v       # Verbose
```

## Code Style

- Follow PEP 8
- Use type hints where possible
- Keep functions focused and small
- Add docstrings to public functions
- Use descriptive variable names

### Example:

```python
def analyze_url(url: str, timeout: int = 8) -> dict[str, Any]:
    """Analyze URL security with timeout.
    
    Args:
        url: URL to analyze
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with analysis results
    """
    # Implementation
```

## Commit Messages

Use clear, descriptive commit messages:

```
feat: add typosquatting detection for brand X
fix: correct redirect loop detection
docs: update installation instructions
perf: optimize metadata extraction
refactor: simplify cache eviction logic
```

Format: `type: description`

Types: feat, fix, docs, style, refactor, perf, test, chore

## Pull Request Process

1. Update README.md with any new features
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG if applicable
5. Keep PR focused on a single feature/fix
6. Add description explaining what and why

## Areas for Contribution

### High Priority
- Additional threat detection rules
- Extended metadata format support
- Performance optimizations
- Security improvements
- Frontend enhancements

### Medium Priority
- Additional external intelligence sources
- Better error messages
- Improved logging
- Docker/deployment improvements
- Documentation

### Lower Priority
- UI/UX improvements
- Code cleanup
- Testing improvements
- CI/CD enhancements

## Testing

All new features should have tests:

```python
def test_analyze_url():
    """Test URL analysis."""
    result = analyze_url("https://example.com")
    assert result["available"] is True
    assert "risk_score" in result
```

## Performance Guidelines

- Avoid unbounded loops/recursion
- Use caching for expensive operations
- Profile before and after optimizations
- Consider memory impact
- Keep request timeouts reasonable

## Security Guidelines

- Validate all user input
- Never log sensitive data (API keys, passwords)
- Use environment variables for secrets
- Sanitize error messages
- Keep dependencies updated
- Report security issues privately

## Documentation

Document your changes:

- Update README.md for user-facing changes
- Add docstrings to functions
- Add comments for non-obvious code
- Update this file if changing guidelines

## Questions?

- Check existing issues/PRs
- Open an issue to discuss major changes
- Ask in PRs if you need clarification

## License

By contributing, you agree your work will be licensed under the same license as the project.
