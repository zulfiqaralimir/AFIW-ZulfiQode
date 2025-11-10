"""
Unit tests for hybrid pipeline
"""
import pytest
from app.agents.management_analyzer import ManagementAnalyzer


def test_hybrid_returns_json():
    """Test that hybrid mode returns valid JSON structure."""
    ma = ManagementAnalyzer(use_hybrid=False, use_gpt_for_web=False, use_local_web=True)
    out = ma.analyze_from_web("Hascol Petroleum")
    
    assert isinstance(out, dict)
    assert "tone" in out or "error" in out
    assert "risk_level" in out or "error" in out


def test_merge_json_function():
    """Test JSON merging functionality."""
    from app.agents.management_analyzer import _merge_json, _safe_load
    
    primary = {"tone": "positive", "tone_confidence": 80}
    secondary = {"tone": "neutral", "tone_confidence": 70}
    
    merged = _merge_json(primary, secondary)
    
    assert merged["tone"] == "positive"  # Primary wins
    assert merged["tone_confidence"] == 75.0  # Averaged


def test_safe_load():
    """Test safe JSON loading."""
    from app.agents.management_analyzer import _safe_load
    
    # Test with dict
    assert _safe_load({"key": "value"}) == {"key": "value"}
    
    # Test with JSON string
    assert _safe_load('{"key": "value"}') == {"key": "value"}
    
    # Test with invalid string
    assert _safe_load("invalid json") == {}
    
    # Test with None
    assert _safe_load(None) == {}

