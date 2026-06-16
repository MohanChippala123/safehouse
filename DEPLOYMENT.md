# Deployment Guide

## Quick Start

### Docker
```bash
docker build -t safehouse .
docker run -p 5000:5000 \
  -e VT_API_KEY=your_key \
  -e URLSCAN_KEY=your_key \
  -e GROQ_KEY=your_key \
  safehouse
```

### Docker Compose
```bash
docker-compose up
```

### Manual
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Database
```bash
python -c "from db import init_db; init_db()"
```

## Production
```bash
gunicorn app:app --workers 4 --timeout 120 --bind 0.0.0.0:5000
```

## Environment Variables
- `VT_API_KEY`: VirusTotal API key
- `URLSCAN_KEY`: URLscan.io API key
- `GROQ_KEY`: Groq API key
- `FLASK_DEBUG`: 0 or 1
- `CACHE_TTL`: Cache TTL in seconds (default: 300)
- `MAX_HOPS`: Max redirect hops (default: 10)

## API Endpoints

### Batch Analysis
```bash
POST /api/batch
{"urls": ["https://example.com", "https://test.com"]}
```

### Export Results
```bash
GET /api/export/json
GET /api/export/csv
GET /api/export/html
```

### Statistics
```bash
GET /api/stats
GET /api/history?limit=20
```

## Monitoring
- Logs: stdout (gunicorn default)
- Database: safehouse.db (SQLite)
- Metrics: /api/stats endpoint
