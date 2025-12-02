"""Notification system for capture events."""
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import deque
from config import PST


class NotificationManager:
    """Manages capture notifications for frontend display."""

    def __init__(self, max_notifications: int = 50):
        """Initialize notification manager."""
        self._notifications: deque = deque(maxlen=max_notifications)
        self._lock = threading.Lock()
        self._notification_id = 0

    def add_notification(
        self,
        type: str,
        title: str,
        message: str,
        status: str = "success"
    ) -> int:
        """
        Add a notification.

        Args:
            type: Type of notification (capture_selected, capture_screenshot, error)
            title: Short title for the notification
            message: Detailed message
            status: success, warning, or error

        Returns:
            Notification ID
        """
        with self._lock:
            self._notification_id += 1
            notification = {
                "id": self._notification_id,
                "type": type,
                "title": title,
                "message": message,
                "status": status,
                "timestamp": datetime.now(PST).isoformat(),
                "read": False
            }
            self._notifications.append(notification)
            return self._notification_id

    def get_notifications(
        self,
        since_id: Optional[int] = None,
        unread_only: bool = False,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get notifications.

        Args:
            since_id: Only return notifications after this ID
            unread_only: Only return unread notifications
            limit: Maximum number of notifications to return

        Returns:
            List of notifications (newest first)
        """
        with self._lock:
            result = []
            for notification in reversed(self._notifications):
                if since_id and notification["id"] <= since_id:
                    continue
                if unread_only and notification["read"]:
                    continue
                result.append(notification.copy())
                if len(result) >= limit:
                    break
            return result

    def mark_read(self, notification_id: int) -> bool:
        """Mark a notification as read."""
        with self._lock:
            for notification in self._notifications:
                if notification["id"] == notification_id:
                    notification["read"] = True
                    return True
            return False

    def mark_all_read(self) -> int:
        """Mark all notifications as read. Returns count of marked notifications."""
        with self._lock:
            count = 0
            for notification in self._notifications:
                if not notification["read"]:
                    notification["read"] = True
                    count += 1
            return count

    def clear(self):
        """Clear all notifications."""
        with self._lock:
            self._notifications.clear()


# Global notification manager instance
notification_manager = NotificationManager()
