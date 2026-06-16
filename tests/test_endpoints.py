"""Integration tests for API endpoints."""
import json
from unittest.mock import patch, MagicMock
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestAnalyzeChain:
    def test_valid_url(self, client):
        with patch("app.follow_chain") as mock:
            mock.return_value = ([{"hostname": "example.com", "risk_score": 0, "flags": []}], "")
            resp = client.post("/analyze/chain", json={"url": "https://example.com"})
            assert resp.status_code == 200
            assert "chain" in json.loads(resp.data)

    def test_no_url(self, client):
        resp = client.post("/analyze/chain", json={})
        assert resp.status_code == 400

    def test_invalid_url(self, client):
        resp = client.post("/analyze/chain", json={"url": "not a url"})
        assert resp.status_code == 400

    def test_cache_hit(self, client):
        with patch("app.follow_chain") as mock:
            mock.return_value = ([{"hostname": "x.com", "risk_score": 5, "flags": []}], "")
            client.post("/analyze/chain", json={"url": "https://x.com"})
            resp2 = client.post("/analyze/chain", json={"url": "https://x.com"})
            assert resp2.status_code == 200
            data = json.loads(resp2.data)
            assert data.get("cached") is True
            assert mock.call_count == 1  # Only called once due to cache


class TestAnalyzeFile:
    def test_no_file(self, client):
        resp = client.post("/analyze-file", data={})
        assert resp.status_code == 400
        assert b"No file uploaded" in resp.data

    def test_invalid_extension(self, client):
        resp = client.post("/analyze-file", data={"file": (b"content", "test.exe")})
        assert resp.status_code == 400
        assert b"not supported" in resp.data

    def test_oversized_file(self, client):
        # Simulate content-length header
        resp = client.post(
            "/analyze-file",
            data={"file": (b"x", "test.jpg")},
            environ_base={"CONTENT_LENGTH": str(100 * 1024 * 1024)}
        )
        assert resp.status_code == 413

    def test_valid_image(self, client):
        with patch("app.extract_metadata") as mock:
            mock.return_value = {"available": True, "file_info": {"filename": "test.jpg"}}
            resp = client.post("/analyze-file", data={"file": (b"fake_jpg", "test.jpg")})
            assert resp.status_code == 200


class TestVerdictCard:
    def test_verdict_rendering(self, client):
        with patch("app.follow_chain") as mock_chain:
            mock_chain.return_value = ([{"hostname": "evil.com", "risk_score": 95, "flags": ["phishing"]}], "")
            resp = client.post("/analyze/chain", json={"url": "https://evil.com"})
            assert resp.status_code == 200
            data = json.loads(resp.data)
            assert data["overall_risk"] > 0


class TestErrorHandling:
    def test_malformed_json(self, client):
        resp = client.post("/analyze/chain", data="not json", content_type="application/json")
        assert resp.status_code == 400

    def test_timeout_handling(self, client):
        with patch("app.follow_chain", side_effect=TimeoutError):
            resp = client.post("/analyze/chain", json={"url": "https://slowsite.com"})
            assert resp.status_code == 500
            assert b"failed" in resp.data.lower()
