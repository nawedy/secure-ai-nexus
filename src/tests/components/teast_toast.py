# src/tests/components/test_toast.py

"""
Toast Component Tests
Provides comprehensive testing for toast notification system
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, List
from datetime import datetime

from components.toast import ToastManager, Toast
from utils.animations import AnimationController
from utils.queue import MessageQueue

class TestToastComponent:
    """
    Comprehensive test suite for Toast notification component
    """

    @pytest.fixture
    def toast_manager(self):
        """Create ToastManager instance for testing"""
        return ToastManager()

    @pytest.fixture
    def mock_animation(self):
        """Mock animation controller"""
        return Mock(spec=AnimationController)

    @pytest.fixture
    def mock_queue(self):
        """Mock message queue"""
        return Mock(spec=MessageQueue)

    def test_toast_creation(self, toast_manager):
        """Test toast notification creation"""
        toast = toast_manager.create_toast({
            "message": "Test message",
            "type": "success",
            "duration": 3000
        })

        assert isinstance(toast, Toast)
        assert toast.message == "Test message"
        assert toast.type == "success"
        assert toast.duration == 3000

    @pytest.mark.asyncio
    async def test_toast_display(self, toast_manager, mock_animation):
        """Test toast display functionality"""
        with patch.object(toast_manager, 'animation', mock_animation):
            toast = toast_manager.create_toast({
                "message": "Test message",
                "type": "info"
            })

            await toast_manager.show_toast(toast)
            mock_animation.animate_entrance.assert_called_once()
            assert toast.is_visible is True

    @pytest.mark.asyncio
    async def test_toast_queue(self, toast_manager, mock_queue):
        """Test toast queue management"""
        with patch.object(toast_manager, 'queue', mock_queue):
            toasts = [
                {"message": f"Message {i}", "type": "info"}
                for i in range(3)
            ]

            for toast_data in toasts:
                await toast_manager.queue_toast(toast_data)

            assert mock_queue.size() == 3
            assert mock_queue.peek()["message"] == "Message 0"

    def test_toast_styling(self, toast_manager):
        """Test toast styling based on type"""
        toast_types = ["success", "error", "warning", "info"]

        for type_ in toast_types:
            toast = toast_manager.create_toast({
                "message": f"Test {type_}",
                "type": type_
            })
            styles = toast_manager.get_toast_styles(toast)

            assert styles["class"].startswith(f"toast-{type_}")
            assert "animation" in styles
            assert "position" in styles

    @pytest.mark.asyncio
    async def test_toast_lifecycle(self, toast_manager, mock_animation):
        """Test complete toast lifecycle"""
        with patch.object(toast_manager, 'animation', mock_animation):
            # Create and show toast
            toast = toast_manager.create_toast({
                "message": "Lifecycle test",
                "type": "info",
                "duration": 1000
            })

            await toast_manager.show_toast(toast)
            assert toast.is_visible is True

            # Wait for auto-dismiss
            await toast_manager.wait_for_dismiss(toast)
            mock_animation.animate_exit.assert_called_once()
            assert toast.is_visible is False

    @pytest.mark.asyncio
    async def test_toast_interaction(self, toast_manager):
        """Test toast interaction handlers"""
        toast = toast_manager.create_toast({
            "message": "Interactive toast",
            "type": "info",
            "actions": [
                {"label": "Confirm", "handler": Mock()},
                {"label": "Cancel", "handler": Mock()}
            ]
        })

        # Test action triggers
        await toast_manager.handle_action(toast, "Confirm")
        toast.actions[0]["handler"].assert_called_once()

        # Test dismissal
        await toast_manager.dismiss_toast(toast)
        assert toast.is_visible is False

    def test_toast_accessibility(self, toast_manager):
        """Test toast accessibility features"""
        toast = toast_manager.create_toast({
            "message": "Accessible message",
            "type": "info"
        })

        accessibility = toast_manager.get_accessibility_props(toast)
        assert "role" in accessibility
        assert "aria-live" in accessibility
        assert "aria-atomic" in accessibility
