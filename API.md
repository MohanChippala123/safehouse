# SafeHouse API Documentation

Complete reference for SafeHouse REST API endpoints.

## Base URL

```
http://localhost:5000
```

## Authentication

Currently no authentication required. Use a reverse proxy (nginx, CloudFlare) for production security.

## Content Type

All requests and responses use `application/json`.

## Rate Limiting

Not implemented in application. Configure at reverse proxy level:
- Recommended: 60 requests/minute per IP
- `/analyze` endpoints: 10 requests/minute per IP

## Endpoints

### GET /

Health check / index page.

**Response:**
- `200 OK`: HTML homepage

---

### POST /analyze/chain

Analyze URL redirect chain without external intelligence.

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "chain": [
    {
      "url": "https://example.com",
      "hostname": "example.com",
      "scheme": "https",
      "ip": "93.184.216.34",
      "status_code": 200,
      "headers": {
        "content-type": "text/html; charset=UTF-8",
        "server": "ECS (dcd/24F5)"
      },
      "tls": {
        "issuer": "ISRG X1",
        "age_days": 120,
        "expires_in_days": 245,
        "valid": true
      },
      "domain_age": {
        "age_days": 10000,
        "registrar": "verisglobal.com"
      },
      "asn": {
        "asn": "AS15169",
        "org": "GOOGLE",
        "country": "US"
      },
      "flags": [],
      "risk_score": 0,
      "risk_level": "clean",
      "trusted": true,
      "t_ms": 150
    }
  ],
  "overall_risk": 0,
  "page_analysis": {
    "trackers": [],
    "fingerprints": [],
    "miners": [],
    "script_domains": [],
    "has_threats": false
  },
  "deep": {
    "credentials": {},
    "typosquat": {},
    "deobfuscation": {},
    "verdict": {},
    "graph": {},
    "timeline": {}
  },
  "html_excerpt": "",
  "elapsed": 1.23,
  "cached": false
}
```

**Status Codes:**
- `200 OK`: Analysis completed
- `400 Bad Request`: Invalid URL
- `500 Internal Server Error`: Analysis failed

---

### POST /analyze/intel

Get external intelligence (VirusTotal, URLscan).

**Request:**
```json
{
  "url": "https://example.com",
  "external_intel": true
}
```

**Response:**
```json
{
  "virustotal": {
    "available": true,
    "malicious": 0,
    "suspicious": 0,
    "harmless": 45,
    "undetected": 22
  },
  "urlscan": {
    "available": true,
    "uuid": "12345678-1234-1234-1234-123456789012",
    "report_url": "https://urlscan.io/result/12345678.../",
    "screenshot_url": "https://urlscan.io/screenshots/12345678....png",
    "screenshot_proxy": "/urlscan-screenshot/12345678...",
    "ready": false
  }
}
```

**Query Parameters:**
- `external_intel` (boolean): Enable external intelligence (default: true)

**Status Codes:**
- `200 OK`: Intelligence retrieved
- `400 Bad Request`: Invalid URL
- `503 Service Unavailable`: External service unavailable

---

### POST /analyze/ai

Get AI-powered threat assessment.

**Request:**
```json
{
  "url": "https://example.com",
  "chain": [/* chain data from /analyze/chain */],
  "html_excerpt": "...",
  "external_intel": true
}
```

**Response:**
```json
{
  "ai_analysis": {
    "available": true,
    "purpose": "Legitimate news website",
    "vibe_score": 9,
    "vibe_reason": "Professional news organization",
    "ai_content_detected": false,
    "threat_assessment": "Safe",
    "threat_reason": "No indicators of compromise",
    "journalist_advice": "This is a legitimate source",
    "tags": ["news", "trusted", "safe"]
  }
}
```

**Status Codes:**
- `200 OK`: Analysis completed
- `400 Bad Request`: Invalid input
- `503 Service Unavailable`: Groq API unavailable

---

### POST /analyze

Complete analysis (chain + intel + AI).

**Request:**
```json
{
  "url": "https://example.com",
  "external_intel": true
}
```

**Response:**
Combines responses from `/analyze/chain`, `/analyze/intel`, and `/analyze/ai`.

```json
{
  "chain": [...],
  "overall_risk": 0,
  "page_analysis": {...},
  "deep": {...},
  "virustotal": {...},
  "urlscan": {...},
  "ai_analysis": {...},
  "elapsed": 2.5,
  "cached": false,
  "cached_age": 0
}
```

**Status Codes:**
- `200 OK`: Complete analysis successful
- `400 Bad Request`: Invalid URL
- `500 Internal Server Error`: Analysis failed

---

### POST /analyze-file

Analyze uploaded file for metadata and privacy risks.

**Request:**
Multipart form data:
- `file`: File to analyze (required)
- `external_intel`: Enable AI analysis (optional, default: true)

**Supported File Types:**
- Images: jpg, jpeg, png, gif, tiff, tif, bmp, webp, heic, heif, raw, cr2, nef, arw
- Documents: pdf, doc, docx, xls, xlsx, ppt, pptx
- Media: mp3, mp4, mov, avi, wav

**Response:**
```json
{
  "available": true,
  "file_info": {
    "filename": "document.pdf",
    "filetype": "PDF",
    "mime": "application/pdf",
    "size": "2.5 MB",
    "dimensions": null
  },
  "findings": {
    "gps": {},
    "device": {},
    "author": {
      "Author": "John Doe"
    },
    "location_text": {},
    "identity": {}
  },
  "gps_summary": null,
  "risk_score": 20,
  "risk_flags": [
    "Author/identity info present"
  ],
  "total_fields": 45,
  "all_fields": {
    "Producer": "Microsoft Word",
    "CreateDate": "2024-01-15T10:30:00"
  },
  "ai_analysis": {
    "available": true,
    "summary": "Contains author metadata",
    "privacy_risks": ["Identifies document creator"],
    "threat_level": "low",
    "journalist_advice": "Remove metadata before sharing",
    "strip_metadata": true
  }
}
```

**Status Codes:**
- `200 OK`: Analysis completed
- `400 Bad Request`: No file or unsupported type
- `413 Payload Too Large`: File exceeds 50MB
- `500 Internal Server Error`: Analysis failed

---

### GET /urlscan-result/<scan_id>

Poll URLscan.io results.

**Parameters:**
- `scan_id`: URLscan UUID (path parameter)

**Response:**
```json
{
  "available": true,
  "uuid": "12345678-1234-1234-1234-123456789012",
  "report_url": "https://urlscan.io/result/...",
  "screenshot_url": "https://urlscan.io/screenshots/...",
  "ready": true,
  "verdicts": {...},
  "stats": {...},
  "screenshot_ready": true
}
```

**Status Codes:**
- `200 OK`: Result retrieved
- `400 Bad Request`: Invalid scan ID format
- `404 Not Found`: Scan not found or in progress

---

### GET /urlscan-screenshot/<scan_id>

Proxy URLscan.io screenshot (bypasses CORS).

**Parameters:**
- `scan_id`: URLscan UUID (path parameter)

**Response:**
PNG image binary data.

**Status Codes:**
- `200 OK`: Screenshot returned
- `400 Bad Request`: Invalid scan ID
- `404 Not Found`: Screenshot not available yet
- `503 Service Unavailable`: No API key configured

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Human-readable error message"
}
```

### Common Errors

**400 Bad Request:**
- Invalid or missing URL
- URL exceeds length limit
- Invalid file type
- Malformed request body

**413 Payload Too Large:**
- File upload exceeds 50MB limit

**500 Internal Server Error:**
- Analysis timeout or crash
- External API error
- ExifTool failure

**503 Service Unavailable:**
- API key not configured
- External service down

## Request Timeouts

- Default request timeout: 8 seconds
- External API timeout: 10 seconds
- URLscan polling: Non-blocking (return immediately)

## Caching

Results cached for 5 minutes (configurable via `CACHE_TTL`):
- `cached: true` in response indicates cached result
- `cached_age: <seconds>` shows cache age

## Rate Limiting Recommendations

Implement at reverse proxy (nginx, CloudFlare):

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=1r/s;
limit_req_zone $binary_remote_addr zone=analyze:10m rate=10r/m;

location /analyze {
    limit_req zone=analyze burst=2 nodelay;
    proxy_pass http://backend;
}

location / {
    limit_req zone=api burst=60 nodelay;
    proxy_pass http://backend;
}
```

## Examples

### Analyze a URL with all features

```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "external_intel": true}'
```

### Analyze just the chain (fast)

```bash
curl -X POST http://localhost:5000/analyze/chain \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Upload and analyze a file

```bash
curl -X POST http://localhost:5000/analyze-file \
  -F "file=@document.pdf" \
  -F "external_intel=true"
```

### Poll URLscan results

```bash
curl http://localhost:5000/urlscan-result/12345678-1234-1234-1234-123456789012
```

## Performance

Typical response times:
- `/analyze/chain`: 1-3 seconds
- `/analyze/intel`: 1-2 seconds
- `/analyze`: 2-4 seconds (combined)
- `/analyze-file`: 1-2 seconds

## Changelog

See CHANGELOG.md for API changes and version history.
