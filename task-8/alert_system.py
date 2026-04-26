"""
Alert System

Monitors sensor readings and aggregated metrics to trigger alerts based on thresholds.
Supports both static thresholds and statistical anomaly detection (z-scores).
"""

from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import List, Callable, Optional


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class Alert:
    """Represents a triggered alert."""
    alert_id: str
    sensor_id: str
    severity: AlertSeverity
    message: str
    timestamp: str
    current_value: float
    threshold_value: float
    metric_type: str  # "temperature", "vibration"
    z_score: Optional[float] = None
    
    def to_dict(self):
        return {
            "alert_id": self.alert_id,
            "sensor_id": self.sensor_id,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp,
            "current_value": round(self.current_value, 2),
            "threshold_value": round(self.threshold_value, 2),
            "metric_type": self.metric_type,
            "z_score": round(self.z_score, 2) if self.z_score else None,
        }


class AlertSystem:
    """
    Monitors sensor data and triggers alerts based on configurable thresholds.
    
    Supports:
    - Static value thresholds (e.g., temp > 100F)
    - Statistical anomalies (e.g., z-score > 3.0)
    - Custom alert handlers
    """
    
    def __init__(self):
        self.alert_history: List[Alert] = []
        self.active_alerts: dict = {}  # sensor_id -> set of active alert types
        self.alert_handlers: List[Callable[[Alert], None]] = []
        self.next_alert_id = 1000
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Register a callback to handle triggered alerts."""
        self.alert_handlers.append(handler)
    
    def check_thresholds(self, sensor_id: str, temperature: float, vibration: float,
                        avg_temp: float, avg_vibration: float,
                        z_score_temp: float, z_score_vibration: float,
                        temp_threshold: float = 100.0,
                        vib_threshold: float = 0.5,
                        z_score_threshold: float = 3.0) -> Optional[Alert]:
        """
        Check sensor reading against thresholds and trigger alert if needed.
        
        Returns:
            Alert if triggered, None otherwise
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Check temperature threshold
        if temperature > temp_threshold:
            alert = Alert(
                alert_id=f"ALERT-{self.next_alert_id}",
                sensor_id=sensor_id,
                severity=AlertSeverity.CRITICAL,
                message=f"Temperature exceeded threshold (>{temp_threshold}F)",
                timestamp=timestamp,
                current_value=temperature,
                threshold_value=temp_threshold,
                metric_type="temperature",
                z_score=z_score_temp,
            )
            self.next_alert_id += 1
            self._trigger_alert(alert)
            return alert
        
        # Check vibration threshold
        if vibration > vib_threshold:
            alert = Alert(
                alert_id=f"ALERT-{self.next_alert_id}",
                sensor_id=sensor_id,
                severity=AlertSeverity.WARNING if vibration < vib_threshold * 1.5 else AlertSeverity.CRITICAL,
                message=f"Vibration exceeded threshold (>{vib_threshold}g)",
                timestamp=timestamp,
                current_value=vibration,
                threshold_value=vib_threshold,
                metric_type="vibration",
                z_score=z_score_vibration,
            )
            self.next_alert_id += 1
            self._trigger_alert(alert)
            return alert
        
        # Check statistical anomaly (z-score > threshold)
        if abs(z_score_temp) > z_score_threshold and abs(z_score_temp) > 0:
            alert = Alert(
                alert_id=f"ALERT-{self.next_alert_id}",
                sensor_id=sensor_id,
                severity=AlertSeverity.WARNING,
                message=f"Temperature anomaly detected (z-score: {z_score_temp:.1f})",
                timestamp=timestamp,
                current_value=temperature,
                threshold_value=avg_temp + (z_score_threshold * 0),  # Placeholder
                metric_type="temperature",
                z_score=z_score_temp,
            )
            self.next_alert_id += 1
            self._trigger_alert(alert)
            return alert
        
        return None
    
    def _trigger_alert(self, alert: Alert):
        """Process triggered alert through registered handlers."""
        self.alert_history.append(alert)
        
        # Log to console with formatting
        status_icon = "🔴" if alert.severity == AlertSeverity.CRITICAL else "🟡"
        print(f"\n{status_icon} [{alert.severity.value}] {alert.sensor_id} — {alert.message}")
        print(f"      Current: {alert.current_value:.1f} | Threshold: {alert.threshold_value:.1f}", end="")
        if alert.z_score:
            print(f" | Z-score: {alert.z_score:.2f}", end="")
        print()
        
        # Call registered handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                print(f"Error in alert handler: {e}")
    
    def get_recent_alerts(self, limit: int = 10) -> List[Alert]:
        """Get the most recent alerts."""
        return self.alert_history[-limit:]
    
    def clear_alerts(self):
        """Clear alert history."""
        self.alert_history.clear()
        self.active_alerts.clear()


def email_handler(alert: Alert):
    """Example handler: send email notifications."""
    if alert.severity == AlertSeverity.CRITICAL:
        print(f"      [EMAIL] Notification sent to ops-team@factory.com")


def log_handler(alert: Alert):
    """Example handler: log to file."""
    print(f"      [LOG] Alert logged to alert_log.txt")


if __name__ == "__main__":
    system = AlertSystem()
    system.add_alert_handler(email_handler)
    system.add_alert_handler(log_handler)
    
    print("Testing alert system:\n")
    
    # Normal reading
    alert = system.check_thresholds(
        "sensor-T1", 75.0, 0.15, 72.0, 0.12, 0.5, 0.8,
        temp_threshold=100, vib_threshold=0.5
    )
    print(f"Normal reading: {'ALERT' if alert else 'OK'}")
    
    # Temperature threshold exceeded
    alert = system.check_thresholds(
        "sensor-T1", 105.0, 0.15, 82.0, 0.12, 2.5, 0.8,
        temp_threshold=100, vib_threshold=0.5
    )
    print(f"High temp: {'ALERT' if alert else 'OK'}")
