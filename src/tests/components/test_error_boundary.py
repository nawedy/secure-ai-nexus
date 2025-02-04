# src/tests/components/test_error_boundary.py

"""
Error Boundary Component Tests
Provides comprehensive testing for error handling components
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from components.error_boundary import ErrorBoundary
from monitoring.error_tracking import ErrorTracker
from utils.logging import Logger

class TestErrorBoundary:
    """
    Comprehensive test suite for Error Boundary component
    """

    @pytest.fixture
    def error_boundary(self):
        """Create ErrorBoundary instance for testing"""
        return ErrorBoundary()

    @pytest.fixture
    def mock_error_tracker(self):
        """Mock error tracking system"""
        return Mock(spec=ErrorTracker)

    @pytest.fixture
    def mock_logger(self):
        """Mock logger"""
        return Mock(spec=Logger)

    def test_error_catching(self, error_boundary):
        """Test error catching functionality"""
        def problematic_component():
            raise ValueError("Test error")

        result = error_boundary.wrap(problematic_component)
        assert error_boundary.has_caught_error()
        assert isinstance(error_boundary.get_error(), ValueError)

    def test_error_recovery(self, error_boundary):
        """Test error recovery mechanisms"""
        error_boundary.catch_error(ValueError("Test error"))
        assert error_boundary.has_caught_error()

        error_boundary.reset()
        assert not error_boundary.has_caught_error()
        assert error_boundary.get_error() is None

    @pytest.mark.asyncio
    async def test_error_reporting(self, error_boundary, mock_error_tracker):
        """Test error reporting functionality"""
        with patch.object(error_boundary, 'error_tracker', mock_error_tracker):
            error = ValueError("Test error")
            error_boundary.catch_error(error)

            await error_boundary.report_error()
            mock_error_tracker.track_error.assert_called_once_with(error)

    def test_fallback_rendering(self, error_boundary):
        """Test fallback UI rendering"""
        error_boundary.catch_error(ValueError("Test error"))
        fallback_ui = error_boundary.render_fallback()

        assert "error-message" in fallback_ui
        assert "retry-button" in fallback_ui
        assert fallback_ui["visible"] is True

    @pytest.mark.asyncio
    async def test_retry_mechanism(self, error_boundary):
        """Test retry mechanism"""
        mock_component = Mock()
        error_boundary.catch_error(ValueError("Test error"))

        await error_boundary.retry()
        assert not error_boundary.has_caught_error()
        mock_component.assert_called_once()

    def test_error_boundary_lifecycle(self, error_boundary):
        """Test error boundary lifecycle"""
        # Test initialization
        assert not error_boundary.has_caught_error()

        # Test error catching
        error_boundary.catch_error(ValueError("Test error"))
        assert error_boundary.has_caught_error()

        # Test cleanup
        error_boundary.cleanup()
        assert not error_boundary.has_caught_error()
        assert error_boundary.get_error() is None

    @pytest.mark.asyncio
    async def test_error_handling_with_children(self, error_boundary):
        """Test error handling with nested components"""
        child_components = [
            Mock(side_effect=ValueError("Child error")),
            Mock(return_value={"type": "div"})
        ]

        results = await error_boundary.render_children(child_components)
        assert error_boundary.has_caught_error()
        assert len(results) == 1  # Only successful component rendered
