"""
Alert Service - Notification and alert management.

Handles:
- Real-time alerts via WebSocket
- Email notifications (critical alerts)
- Alert history in database
"""

from typing import Dict
from uuid import UUID, uuid4
from datetime import datetime

from backend.core.event_emitter import get_event_emitter


class AlertService:
    """Service for managing alerts and notifications."""

    def __init__(self):
        self.event_emitter = get_event_emitter()
        self.alert_history: Dict[UUID, list] = {}  # project_id -> alerts

    async def send_alert(
        self,
        project_id: UUID,
        alert_type: str,
        title: str,
        message: str,
        severity: str = "info",
        actions: list = None,
        metadata: dict = None,
    ) -> str:
        """
        Send alert to user(s).

        Args:
            project_id: Project UUID
            alert_type: Type of alert (circular_deps, high_complexity, etc)
            title: Alert title
            message: Alert message
            severity: critical|error|warning|info
            actions: Suggested actions
            metadata: Additional data

        Returns:
            Alert ID
        """
        alert_id = str(uuid4())

        alert = {
            "id": alert_id,
            "project_id": str(project_id),
            "type": alert_type,
            "severity": severity,
            "title": title,
            "message": message,
            "actions": actions or [],
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
            "read": False,
        }

        # Emit to real-time listeners (WebSocket)
        self.event_emitter.emit("alert", alert)

        # Store in history
        if project_id not in self.alert_history:
            self.alert_history[project_id] = []
        self.alert_history[project_id].append(alert)

        # Send email if critical
        if severity == "critical":
            await self._send_email_alert(alert)

        # TODO: Save to database for persistence
        # await self._save_alert_to_db(alert)

        return alert_id

    async def _send_email_alert(self, alert: dict) -> None:
        """Send email notification for critical alerts."""
        # TODO: Implement email sending
        # For now, just log
        print(f"📧 Would send email for critical alert: {alert['title']}")

    async def get_project_alerts(
        self,
        project_id: UUID,
        unread_only: bool = False,
        severity: str = None,
    ) -> list:
        """Get alerts for project."""
        alerts = self.alert_history.get(project_id, [])

        # Filter
        if unread_only:
            alerts = [a for a in alerts if not a["read"]]

        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]

        return alerts

    async def mark_alert_read(self, project_id: UUID, alert_id: str) -> bool:
        """Mark alert as read."""
        alerts = self.alert_history.get(project_id, [])

        for alert in alerts:
            if alert["id"] == alert_id:
                alert["read"] = True
                return True

        return False

    async def clear_project_alerts(self, project_id: UUID) -> None:
        """Clear all alerts for project."""
        if project_id in self.alert_history:
            del self.alert_history[project_id]


# ============================================================================
# Global Instance
# ============================================================================

_alert_service: AlertService = None


def get_alert_service() -> AlertService:
    """Get global alert service instance."""
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service


# ============================================================================
# Convenience Functions
# ============================================================================


async def send_alert(
    project_id: UUID,
    alert_type: str,
    title: str,
    message: str,
    severity: str = "info",
    actions: list = None,
) -> str:
    """
    Convenience function to send alert.

    Usage:
        await send_alert(
            project_id,
            "high_complexity",
            "High Complexity",
            "Architecture complexity > 80",
            severity="warning"
        )
    """
    service = get_alert_service()
    return await service.send_alert(project_id, alert_type, title, message, severity, actions)
