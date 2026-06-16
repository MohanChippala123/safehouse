# Quick Start Guide

Get SafeHouse running in 5 minutes.

## Prerequisites

- Python 3.12+
- ExifTool (optional but recommended)

## Setup

### 1. Clone & Enter Directory

```bash
git clone <repo-url>
cd safehouse-improved/yes-improved
```

### 2. Run Setup Script

**Windows:**
```bash
python setup.py
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python setup.py
source venv/bin/activate
```

### 3. Configure API Keys (Optional)

```bash
cp .env.example .env
# Edit .env and add your API keys:
# - VT_API_KEY from virustotal.com
# - URLSCAN_KEY from urlscan.io
# - GROQ_KEY from console.groq.com
```

### 4. Run the App

```bash
python app.py
```

Visit http://localhost:5000

---

## Using the Web Interface

### Analyze a URL

1. Enter a URL in the input field
2. Click "Analyze"
3. Wait for results (1-5 seconds)
4. Review findings:
   - Redirect chain
   - Security risks
   - Trackers
   - Threat verdict

### Analyze a File

1. Click "Analyze File"
2. Upload an image, PDF, or Office document
3. Review metadata findings:
   - Author/creator info
   - GPS location (if embedded)
   - Device information
   - Risk assessment

---

## Using the API

### Analyze a URL

```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Analyze a File

```bash
curl -X POST http://localhost:5000/analyze-file \
  -F "file=@myfile.pdf"
```

See [API.md](API.md) for complete API reference.

---

## Docker

### Run with Docker

```bash
docker build -t safehouse .
docker run -p 5000:5000 safehouse
```

### Development with Docker Compose

```bash
docker-compose up
```

---

## Common Commands

```bash
make dev-server    # Run development server
make test          # Run tests
make lint          # Check code style
make format        # Auto-format code
make clean         # Clean cache
make docker-dev    # Run with Docker
```

See [Makefile](Makefile) for all commands.

---

## Troubleshooting

### Port 5000 already in use?

```bash
# Find what's using it
lsof -i :5000
# Kill it
kill -9 <pid>
```

### ImportError for exiftool?

```bash
# Install ExifTool:
# Windows: choco install exiftool
# macOS: brew install exiftool
# Linux: apt-get install libimage-exiftool-perl
```

### API keys not working?

1. Verify keys in `.env` (not `.env.example`)
2. Check API key is valid in service dashboard
3. Check rate limits aren't exceeded

### Still having issues?

1. Check [README.md](README.md) troubleshooting section
2. Review [DEVELOPMENT.md](DEVELOPMENT.md) for debugging
3. Check [SECURITY.md](SECURITY.md) for deployment issues

---

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [API.md](API.md) for API reference
- Review [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- See [SECURITY.md](SECURITY.md) for production deployment

---

## Features at a Glance

✅ Redirect chain analysis  
✅ TLS certificate validation  
✅ Domain age & registrar checks  
✅ Typosquatting detection  
✅ Tracker detection  
✅ Credential form detection  
✅ File metadata extraction  
✅ VirusTotal integration  
✅ URLscan.io integration  
✅ AI threat assessment  

---

That's it! You're ready to analyze URLs and files for security threats.
