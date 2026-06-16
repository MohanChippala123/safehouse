"""Tests for app.py endpoints."""

import json
from unittest.mock import patch

import pytest

from app import app, normalize_url


@pytest.fixture
def client():
    """Create test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index(client):
    """Test index route."""
    response = client.get("/")
    assert response.status_code == 200


def test_normalize_url_valid():
    """Test URL normalization with valid URLs."""
    assert normalize_url("example.com") == "https://example.com"
    assert normalize_url("https://example.com") == "https://example.com"
    assert normalize_url("http://example.com") == "http://example.com"
    assert normalize_url("  https://example.com  ") == "https://example.com"


def test_normalize_url_invalid():
    """Test URL normalization with invalid URLs."""
    with pytest.raises(ValueError, match="No URL provided"):
        normalize_url("")

    with pytest.raises(ValueError, match="exceeds maximum length"):
        normalize_url("https://" + "a" * 2100)

    with pytest.raises(ValueError, match="Could not parse"):
        normalize_url("http://")

    with pytest.raises(ValueError, match="Invalid hostname"):
        normalize_url("http://.example.com")


def test_analyze_chain_no_url(client):
    """Test /analyze/chain without URL."""
    response = client.post("/analyze/chain", json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_analyze_chain_invalid_url(client):
    """Test /analyze/chain with invalid URL."""
    response = client.post("/analyze/chain", json={"url": "not a url"})
    assert response.status_code == 400


@patch("app.follow_chain")
def test_analyze_chain_success(mock_chain, client):
    """Test successful /analyze/chain."""
    mock_chain.return_value = (
        [{"hostname": "example.com", "risk_score": 0, "flags": []}],
        ""
    )
    response = client.post("/analyze/chain", json={"url": "https://example.com"})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "chain" in data
    assert "overall_risk" in data


def test_analyze_intel_disabled(client):
    """Test /analyze/intel with external_intel disabled."""
    response = client.post(
        "/analyze/intel",
        json={"url": "https://example.com", "external_intel": False}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["virustotal"]["available"] is False
    assert data["urlscan"]["available"] is False


def test_analyze_file_no_file(client):
    """Test /analyze-file without file."""
    response = client.post("/analyze-file", data={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_analyze_file_invalid_type(client):
    """Test /analyze-file with invalid file type."""
    response = client.post(
        "/analyze-file",
        data={"file": (b"content", "test.exe")}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "not supported" in data["error"]


def test_urlscan_result_invalid_id(client):
    """Test /urlscan-result with invalid ID."""
    response = client.get("/urlscan-result/invalid")
    assert response.status_code == 400


def test_urlscan_result_valid_id(client):
    """Test /urlscan-result with valid ID format."""
    # Valid scan ID format
    response = client.get("/urlscan-result/12345678-1234-1234-1234-123456789012")
    assert response.status_code in (200, 404)  # May not exist but format is valid
