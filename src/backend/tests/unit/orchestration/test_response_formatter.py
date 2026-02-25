"""
Tests for response formatter.
"""

import pytest

from app.orchestration.response_formatter import ResponseFormatter


class TestResponseFormatterSanitization:
    """Test response sanitization logic."""

    def test_sanitize_response_removes_according_to_context(self):
        """Test that 'according to the context' is removed."""
        formatter = ResponseFormatter()
        
        response = "According to the provided context, you need AOW certification."
        sanitized = formatter.sanitize_response(response)
        
        assert "according to" not in sanitized.lower()
        assert "provided context" not in sanitized.lower()
        assert "AOW certification" in sanitized
        assert "you need" in sanitized

    def test_sanitize_response_removes_based_on_information(self):
        """Test that 'based on the provided information' is removed."""
        formatter = ResponseFormatter()
        
        response = "Based on the provided information, wreck diving requires Advanced Open Water."
        sanitized = formatter.sanitize_response(response)
        
        assert "based on" not in sanitized.lower()
        assert "provided information" not in sanitized.lower()
        assert "wreck diving requires" in sanitized

    def test_sanitize_response_removes_bracketed_sources(self):
        """Test that bracketed citations are removed."""
        formatter = ResponseFormatter()
        
        response = "Wreck diving requires AOW [Source: certifications/padi/aow.md]. It's an exciting specialty."
        sanitized = formatter.sanitize_response(response)
        
        assert "[Source:" not in sanitized
        assert "Wreck diving requires AOW" in sanitized
        assert "It's an exciting specialty" in sanitized

    def test_sanitize_response_removes_from_documentation(self):
        """Test that 'from the documentation' is removed."""
        formatter = ResponseFormatter()
        
        response = "From the documentation, you'll need 20 logged dives for this certification."
        sanitized = formatter.sanitize_response(response)
        
        assert "from the documentation" not in sanitized.lower()
        assert "you'll need 20 logged dives" in sanitized

    def test_sanitize_response_removes_in_the_document(self):
        """Test that 'in the document' is removed."""
        formatter = ResponseFormatter()
        
        response = "In the document, it mentions that DAN insurance is recommended."
        sanitized = formatter.sanitize_response(response)
        
        assert "in the document" not in sanitized.lower()
        assert "DAN insurance is recommended" in sanitized

    def test_sanitize_response_removes_context_shows(self):
        """Test that 'the context shows' is removed."""
        formatter = ResponseFormatter()
        
        response = "The retrieved context shows that Tioman has great visibility year-round."
        sanitized = formatter.sanitize_response(response)
        
        assert "context shows" not in sanitized.lower()
        assert "retrieved" not in sanitized.lower()
        assert "Tioman has great visibility" in sanitized

    def test_sanitize_response_removes_parenthetical_sources(self):
        """Test that parenthetical sources are removed."""
        formatter = ResponseFormatter()
        
        response = "Advanced Open Water (Source: padi-certifications.md) is required for deep dives."
        sanitized = formatter.sanitize_response(response)
        
        assert "(Source:" not in sanitized
        assert "Advanced Open Water is required" in sanitized

    def test_sanitize_response_preserves_clean_text(self):
        """Test that clean responses pass through unchanged."""
        formatter = ResponseFormatter()
        
        response = "Wreck diving requires Advanced Open Water certification and 20+ logged dives."
        sanitized = formatter.sanitize_response(response)
        
        assert sanitized == response

    def test_sanitize_response_handles_empty_string(self):
        """Test handling of empty string."""
        formatter = ResponseFormatter()
        
        sanitized = formatter.sanitize_response("")
        assert sanitized == ""

    def test_sanitize_response_handles_none(self):
        """Test handling of None."""
        formatter = ResponseFormatter()
        
        sanitized = formatter.sanitize_response(None)
        assert sanitized is None

    def test_sanitize_response_cleans_extra_whitespace(self):
        """Test that extra whitespace is cleaned up after removal."""
        formatter = ResponseFormatter()
        
        response = "According to the provided context,  you need AOW certification."
        sanitized = formatter.sanitize_response(response)
        
        # Should not have double spaces
        assert "  " not in sanitized
        assert sanitized.strip() == sanitized

    def test_sanitize_response_cleans_duplicate_punctuation(self):
        """Test that duplicate punctuation is cleaned."""
        formatter = ResponseFormatter()
        
        response = "Based on the context,, you need certification."
        sanitized = formatter.sanitize_response(response)
        
        assert ",," not in sanitized
        assert "you need certification" in sanitized

    def test_sanitize_response_case_insensitive(self):
        """Test that pattern matching is case-insensitive."""
        formatter = ResponseFormatter()
        
        response = "ACCORDING TO THE PROVIDED CONTEXT, you need AOW."
        sanitized = formatter.sanitize_response(response)
        
        assert "according to" not in sanitized.lower()
        assert "you need AOW" in sanitized

    def test_sanitize_response_multiple_patterns(self):
        """Test removal of multiple patterns in one response."""
        formatter = ResponseFormatter()
        
        response = (
            "According to the provided context, wreck diving requires AOW [Source: padi.md]. "
            "From the documentation, you'll also need 20 dives."
        )
        sanitized = formatter.sanitize_response(response)
        
        assert "according to" not in sanitized.lower()
        assert "[Source:" not in sanitized
        assert "from the documentation" not in sanitized.lower()
        assert "wreck diving requires AOW" in sanitized
        assert "you'll also need 20 dives" in sanitized

    def test_sanitize_response_preserves_natural_language(self):
        """Test that natural conversational references are preserved."""
        formatter = ResponseFormatter()
        
        # These should NOT be removed - they're natural language, not RAG leaks
        response = "Based on your experience level, I'd recommend starting with Open Water."
        sanitized = formatter.sanitize_response(response)
        
        # "Based on your experience" should remain (not a RAG reference)
        assert "Based on your experience" in sanitized
