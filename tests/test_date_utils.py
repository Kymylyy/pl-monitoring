"""Testy dla modułu date_utils."""

from datetime import datetime

import pytest

from pl_monitoring.utils.date_utils import parse_date, parse_polish_date


class TestParsePolishDate:
    """Testy dla funkcji parse_polish_date."""
    
    def test_valid_date(self):
        """Test parsowania poprawnej daty."""
        result = parse_polish_date("15-01-2025")
        assert result == datetime(2025, 1, 15)
    
    def test_invalid_date(self):
        """Test parsowania niepoprawnej daty."""
        result = parse_polish_date("invalid")
        assert result is None
    
    def test_empty_string(self):
        """Test parsowania pustego stringa."""
        result = parse_polish_date("")
        assert result is None
    
    def test_whitespace(self):
        """Test parsowania daty z białymi znakami."""
        result = parse_polish_date("  15-01-2025  ")
        assert result == datetime(2025, 1, 15)


class TestParseDate:
    """Testy dla funkcji parse_date."""
    
    def test_date_with_time(self):
        """Test parsowania daty z czasem."""
        result = parse_date("2025-01-15 14:30")
        assert result == datetime(2025, 1, 15, 14, 30)
    
    def test_date_without_time(self):
        """Test parsowania daty bez czasu."""
        result = parse_date("2025-01-15")
        assert result == datetime(2025, 1, 15)
    
    def test_invalid_date(self):
        """Test parsowania niepoprawnej daty."""
        result = parse_date("invalid")
        assert result is None
    
    def test_empty_string(self):
        """Test parsowania pustego stringa."""
        result = parse_date("")
        assert result is None

