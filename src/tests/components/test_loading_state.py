# src/tests/components/test_loading_state.py

"""
Loading State Component Tests
Provides comprehensive testing for loading state management
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, List
from datetime import datetime

from components.loading import LoadingStateManager, LoadingState
from utils.animations import AnimationController
from monitoring.performance import PerformanceMonitor

class TestLoadingState:
    """
    Comprehensive test suite for Loading State component
    """

    @pytest.fixture
    def loading_manager(self):
        """Create LoadingStateManager instance for testing"""
        return LoadingStateManager()

    @pytest.fixture
    def mock_animation(self):
        """Mock animation controller"""
        return Mock(spec=AnimationController)

    @pytest.fixture
    def mock_monitor(self):
        """Mock performance monitor"""
        return Mock(spec=PerformanceMonitor)

    def test_loading_state_creation(self, loading_manager):
        """Test loading state creation"""
        state = loading_manager.create_loading_state({
            "id": "test-loader",
            "type": "spinner",
            "message": "Loading...",
            "cancelable": True
        })

        assert isinstance(state, LoadingState)
        assert state.id == "test-loader"
        assert state.type == "spinner"
        assert state.message == "Loading..."
        assert state.cancelable is True

    @pytest.mark.asyncio
    async def test_loading_state_transitions(self, loading_manager, mock_animation):
        """Test loading state transitions"""
        with patch.object(loading_manager, 'animation', mock_animation):
            state = loading_manager.create_loading_state({
                "id": "transition-test",
                "type": "spinner"
            })

            # Test show transition
            await loading_manager.show_loading(state)
            mock_animation.animate_entrance.assert_called_once()
            assert state.is_visible is True

            # Test hide transition
            await loading_manager.hide_loading(state)
            mock_animation.animate_exit.assert_called_once()
            assert state.is_visible is False

    @pytest.mark.asyncio
    async def test_loading_progress(self, loading_manager):
        """Test loading progress updates"""
        state = loading_manager.create_loading_state({
            "id": "progress-test",
            "type": "progress",
            "total": 100
        })

        # Test progress updates
        await loading_manager.update_progress(state, 50)
        assert state.progress == 50
        assert state.percentage == 50.0

        # Test completion
        await loading_manager.update_progress(state, 100)
        assert state.is_complete is True

    def test_loading_state_styling(self, loading_manager):
        """Test loading state styling"""
        state_types = ["spinner", "progress", "skeleton", "pulse"]

        for type_ in state_types:
            state = loading_manager.create_loading_state({
                "id": f"{type_}-test",
                "type": type_
            })
            styles = loading_manager.get_loading_styles(state)

            assert styles["class"].startswith(f"loading-{type_}")
            assert "animation" in styles
            assert "visibility" in styles

    @pytest.mark.asyncio
    async def test_loading_timeout(self, loading_manager, mock_monitor):
        """Test loading timeout handling"""
        with patch.object(loading_manager, 'monitor', mock_monitor):
            state = loading_manager.create_loading_state({
                "id": "timeout-test",
                "timeout": 1000
            })

            await loading_manager.show_loading(state)
            await loading_manager.wait_with_timeout(state)

            assert state.has_timed_out is True
            mock_monitor.record_timeout.assert_called_once()

    @pytest.mark.asyncio
    async def test_loading_cancellation(self, loading_manager):
        """Test loading cancellation"""
        state = loading_manager.create_loading_state({
            "id": "cancel-test",
            "cancelable": True
        })

        cancel_handler = Mock()
        state.on_cancel = cancel_handler

        await loading_manager.cancel_loading(state)
        cancel_handler.assert_called_once()
        assert state.is_cancelled is True

    def test_loading_accessibility(self, loading_manager):
        """Test loading state accessibility"""
        state = loading_manager.create_loading_state({
            "id": "accessibility-test",
            "message": "Loading content"
        })

        accessibility = loading_manager.get_accessibility_props(state)
        assert "role" in accessibility
        assert "aria-busy" in accessibility
        assert "aria-label" in accessibility
