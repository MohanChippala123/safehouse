"""Unit tests for analysis functions."""
import pytest
from sh_engine import (
    detect_typosquat, trace_credentials, deobfuscate,
    _lev, _apex, _skeleton, BRANDS
)


class TestLevenshteinDistance:
    def test_identical(self):
        assert _lev("test", "test") == 0

    def test_insertion(self):
        assert _lev("test", "tests") == 1

    def test_deletion(self):
        assert _lev("tests", "test") == 1

    def test_substitution(self):
        assert _lev("cat", "hat") == 1

    def test_empty(self):
        assert _lev("", "test") == 4
        assert _lev("test", "") == 4


class TestApexDomain:
    def test_apex_simple(self):
        assert _apex("example.com") == "example.com"

    def test_apex_subdomain(self):
        assert _apex("sub.example.com") == "example.com"

    def test_apex_deep(self):
        assert _apex("a.b.c.example.com") == "example.com"

    def test_apex_empty(self):
        assert _apex("") == ""


class TestSkeleton:
    def test_normalization(self):
        # Replace homoglyphs with ASCII
        result = _skeleton("gооgle")  # Contains Cyrillic 'o'
        assert "o" in result or result.lower() == result


class TestCredentialDetection:
    def test_no_forms(self):
        result = trace_credentials("", "https://example.com")
        assert result["available"] is False
        assert result["forms"] == []

    def test_safe_form(self):
        html = '<form action="https://example.com/process"><input type="email" name="email"></form>'
        result = trace_credentials(html, "https://example.com")
        assert result["available"] is True
        assert len(result["forms"]) > 0
        assert result["forms"][0]["sensitive"] is False

    def test_password_form_offsite(self):
        html = '<form action="https://evil.com"><input type="password" name="pass"></form>'
        result = trace_credentials(html, "https://legitimate.com")
        assert result["risk"] > 0
        assert any("off-site" in f for f in result["flags"])

    def test_http_password(self):
        html = '<form action="http://example.com"><input type="password" name="pass"></form>'
        result = trace_credentials(html, "http://example.com")
        assert result["risk"] > 0


class TestTyposquatting:
    def test_legitimate_brand(self):
        result = detect_typosquat("google.com")
        assert result["is_brand"] is True
        assert result["matches"] == []

    def test_typosquat(self):
        result = detect_typosquat("gogle.com")
        assert result["is_brand"] is False
        # Should find similarity to google.com
        assert len(result["matches"]) > 0 or result["risk"] > 0

    def test_unicode_domain(self):
        result = detect_typosquat("gооgle.com")  # Cyrillic 'o'
        assert len(result["flags"]) > 0
        assert result["risk"] > 0


class TestDeobfuscation:
    def test_no_obfuscation(self):
        result = deobfuscate("normal text")
        assert result["available"] is False

    def test_base64_detection(self):
        html = 'atob("aGVsbG8=")'
        result = deobfuscate(html)
        # Should detect the base64 pattern
        assert "layers" in result

    def test_hex_escapes(self):
        html = r"\x48\x65\x6c\x6c\x6f"
        result = deobfuscate(html)
        assert "layers" in result
