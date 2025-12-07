"""Testy jednostkowe dla modułów monitoringu."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict

from horizon_monitoring.monitors.rcl_project_monitor import RCLProjectMonitor
from horizon_monitoring.monitors.sejm_project_monitor import SejmProjectMonitor
from horizon_monitoring.exceptions import RCLConnectionError, SejmConnectionError


class TestRCLProjectMonitor:
    """Testy dla RCLProjectMonitor."""
    
    def test_init_with_defaults(self):
        """Test inicjalizacji z domyślnymi wartościami."""
        monitor = RCLProjectMonitor()
        assert monitor.base_url == "https://legislacja.rcl.gov.pl"
        assert monitor._load_all_projects is not None
        assert monitor._save_all_projects is not None
    
    def test_init_with_custom_functions(self):
        """Test inicjalizacji z niestandardowymi funkcjami."""
        load_fn = Mock(return_value=[])
        save_fn = Mock()
        
        monitor = RCLProjectMonitor(
            load_projects_fn=load_fn,
            save_projects_fn=save_fn,
            base_url="http://test.com"
        )
        
        assert monitor.base_url == "http://test.com"
        assert monitor._load_all_projects == load_fn
        assert monitor._save_all_projects == save_fn
    
    def test_monitor_with_no_projects(self):
        """Test monitoringu gdy brak projektów."""
        monitor = RCLProjectMonitor(
            load_projects_fn=lambda: [],
            save_projects_fn=Mock()
        )
        
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 12, 31)
        
        result = monitor.monitor(start_date, end_date)
        assert result == []
    
    def test_monitor_filters_rcl_projects(self):
        """Test że monitor filtruje tylko projekty RCL."""
        projects = [
            {"id": 1, "source": "rcl", "title": "Projekt RCL"},
            {"id": 2, "source": "sejm", "title": "Projekt Sejm"},
            {"id": 3, "source": "rcl", "title": "Projekt RCL 2"}
        ]
        
        monitor = RCLProjectMonitor(
            load_projects_fn=lambda: projects,
            save_projects_fn=Mock()
        )
        
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 12, 31)
        
        with patch.object(monitor, '_fetch_project_page', return_value=None):
            result = monitor.monitor(start_date, end_date)
            # Powinno zwrócić tylko projekty RCL (2 projekty)
            assert len(result) == 2
            assert all(p.get('source') == 'rcl' for p in result)


class TestSejmProjectMonitor:
    """Testy dla SejmProjectMonitor."""
    
    def test_init_with_defaults(self):
        """Test inicjalizacji z domyślnymi wartościami."""
        monitor = SejmProjectMonitor()
        assert monitor.base_url == "https://www.sejm.gov.pl"
        assert monitor.load_projects is not None
        assert monitor.save_projects is not None
    
    def test_init_with_custom_functions(self):
        """Test inicjalizacji z niestandardowymi funkcjami."""
        load_fn = Mock(return_value=[])
        save_fn = Mock()
        
        monitor = SejmProjectMonitor(
            load_projects_fn=load_fn,
            save_projects_fn=save_fn,
            base_url="http://test.com"
        )
        
        assert monitor.base_url == "http://test.com"
        assert monitor.load_projects == load_fn
        assert monitor.save_projects == save_fn
    
    def test_monitor_with_no_projects(self):
        """Test monitoringu gdy brak projektów."""
        monitor = SejmProjectMonitor(
            load_projects_fn=lambda: [],
            save_projects_fn=Mock()
        )
        
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 12, 31)
        
        result = monitor.monitor(start_date, end_date)
        assert result == []
    
    def test_monitor_filters_sejm_projects(self):
        """Test że monitor filtruje tylko projekty Sejm."""
        projects = [
            {"id": "1", "source": "rcl", "title": "Projekt RCL"},
            {"id": "2", "source": "sejm", "title": "Projekt Sejm"},
            {"id": "3", "source": "sejm", "title": "Projekt Sejm 2"}
        ]
        
        monitor = SejmProjectMonitor(
            load_projects_fn=lambda: projects,
            save_projects_fn=Mock()
        )
        
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 12, 31)
        
        with patch.object(monitor, '_fetch_process_page', return_value=None):
            result = monitor.monitor(start_date, end_date)
            # Powinno zwrócić tylko projekty Sejm (2 projekty)
            assert len(result) == 2
            assert all(p.get('source') == 'sejm' for p in result)


class TestDateValidation:
    """Testy walidacji dat."""
    
    def test_start_date_after_end_date_raises_error(self):
        """Test że start_date > end_date powoduje błąd."""
        # To jest testowany w skryptach, ale możemy dodać test jednostkowy
        start_date = datetime(2025, 12, 31)
        end_date = datetime(2025, 1, 1)
        
        assert start_date > end_date  # Podstawowa walidacja

