# Development Guide

Guide for developers contributing to or extending SafeHouse.

## Quick Start

```bash
# Set up environment
python setup.py

# Or manually:
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy .env
cp .env.example .env

# Run development server
make dev-server
```

Visit http://localhost:5000

## Project Structure

```
safehouse-improved/
├── yes-improved/                # Main application
│   ├── app.py                   # Flask application and API endpoints
│   ├── sh_engine.py             # Core analysis engine
│   ├── config.py                # Configuration management
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile               # Docker build configuration
│   ├── docker-compose.yml       # Local development Docker setup
│   ├── render.yaml              # Render.com deployment config
│   ├── setup.py                 # Development environment setup
│   ├── pytest.ini               # Test configuration
│   ├── Makefile                 # Development commands
│   ├── templates/               # HTML templates
│   │   └── index.html           # Frontend UI
│   ├── static/                  # Static assets
│   │   ├── css/style.css        # Styles
│   │   └── js/script.js         # Frontend logic
│   ├── tests/                   # Test suite
│   │   ├── test_app.py          # API endpoint tests
│   │   └── test_sh_engine.py    # Analysis engine tests
│   ├── README.md                # User documentation
│   ├── API.md                   # API reference
│   ├── DEVELOPMENT.md           # This file
│   ├── CONTRIBUTING.md          # Contribution guidelines
│   ├── SECURITY.md              # Security guidelines
│   ├── CHANGELOG.md             # Version history
│   └── .env.example             # Environment template
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

Edit code in your preferred editor. SafeHouse works with:
- VS Code
- PyCharm
- Vim/Neovim
- Any text editor

### 3. Run Tests

```bash
make test          # Run all tests
make coverage      # With coverage report
make lint          # Check code style
make format        # Auto-format code
```

### 4. Test Locally

```bash
make dev-server
# Test at http://localhost:5000
```

### 5. Commit and Push

```bash
git add .
git commit -m "feat: add new feature"
git push origin feature/my-feature
```

### 6. Open Pull Request

On GitHub, create a PR with:
- Clear description of changes
- Why the change was made
- How to test it

## Code Style

### Python

Follow PEP 8 with these preferences:
- Line length: 100 characters (black default)
- 4-space indentation
- Type hints where practical
- Docstrings for public functions

### Running Code Formatters

```bash
# Format code automatically
make format

# Or manually:
black app.py sh_engine.py config.py
isort app.py sh_engine.py config.py

# Check without formatting
flake8 app.py sh_engine.py config.py
```

### Type Checking

```bash
make type-check
```

## Testing

### Writing Tests

Tests go in `tests/` directory:

```python
# tests/test_feature.py
import pytest
from app import some_function

def test_basic():
    """Test basic functionality."""
    result = some_function("input")
    assert result == "expected"

@pytest.mark.slow
def test_slow_operation():
    """Test that might take time."""
    # Test code
    pass
```

### Running Tests

```bash
make test                    # All tests
make coverage               # With coverage
pytest tests/test_app.py    # Specific file
pytest -k test_analyze      # Match test name
pytest -m "not slow"        # Skip slow tests
```

## Adding Features

### Example: Add New Analysis Type

1. **Add detection logic** to `sh_engine.py`:
   ```python
   def detect_new_threat(url: str) -> dict:
       """Detect new threat type."""
       # Implementation
       return {"available": True, "threat": "..."}
   ```

2. **Add to verdict** in `build_verdict()`:
   ```python
   new_threat = detect_new_threat(url)
   if new_threat.get("threat"):
       add("New Threat", new_threat["threat"], 20, "medium")
   ```

3. **Add API endpoint** in `app.py`:
   ```python
   @app.route("/analyze/new-threat", methods=["POST"])
   def analyze_new_threat():
       """Detect new threat type."""
       url = parse_analyze_url()
       result = detect_new_threat(url)
       return jsonify(result)
   ```

4. **Add tests** in `tests/test_sh_engine.py`:
   ```python
   def test_detect_new_threat():
       """Test new threat detection."""
       result = detect_new_threat("https://example.com")
       assert result["available"]
   ```

5. **Update documentation**:
   - Add to README.md features list
   - Document API in API.md
   - Add to CHANGELOG.md

### Example: Add New Configuration

1. **Add to `config.py`**:
   ```python
   @dataclass
   class MyConfig:
       my_setting: str = "default"
   ```

2. **Load from environment**:
   ```python
   # In .env.example
   MY_SETTING=value
   
   # In config.py
   my_setting=os.environ.get("MY_SETTING", "default")
   ```

3. **Use in app.py**:
   ```python
   from config import config
   value = config.my_setting
   ```

## Docker Development

### Build Image

```bash
make docker-build
```

### Run Container

```bash
# Production mode
make docker-run

# Development mode
make docker-dev
```

### Debug Container

```bash
docker run -it --entrypoint /bin/bash safehouse:latest
# Inside container:
python app.py
```

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

# In your code:
profiler = cProfile.Profile()
profiler.enable()
# Code to profile
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Memory Profiling

```bash
pip install memory_profiler
python -m memory_profiler app.py
```

### Common Bottlenecks

1. **External API calls**: Use concurrent.futures
2. **Regex matching**: Pre-compile patterns
3. **File I/O**: Use streaming for large files
4. **Network requests**: Use connection pooling

## Debugging

### Print Debugging

```python
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug info: %s", variable)
```

### Interactive Debugging

```python
import pdb; pdb.set_trace()
# Or in Python 3.7+:
breakpoint()
```

### IDE Debugging

Set breakpoints in VS Code or PyCharm and run:
```bash
python -m debugpy --listen 5678 app.py
```

## Deployment

### Local Testing

```bash
make run  # Production gunicorn server
```

### Docker Testing

```bash
make docker-run
```

### Render.com

Push to main branch. Render reads `render.yaml` and deploys automatically.

## Troubleshooting

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

### Cache Issues

```bash
# Clear Python cache
make clean

# Clear pip cache
pip cache purge
```

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill it
kill -9 <pid>
```

### ExifTool Not Found

```bash
# Check installation
which exiftool  # or where exiftool on Windows

# Reinstall
brew install exiftool  # macOS
choco install exiftool # Windows
apt-get install libimage-exiftool-perl # Linux
```

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Requests Library](https://requests.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)

## Getting Help

- Check existing issues and PRs
- Review code comments and docstrings
- Ask in pull request discussions
- Email maintainer for security issues

## Releasing

1. Update version in code
2. Update CHANGELOG.md
3. Tag release: `git tag v1.0.0`
4. Push: `git push origin main --tags`
5. Create GitHub release with notes

## Future Improvements

See CHANGELOG.md "Future Improvements" section for planned features.
