"""
Windowed Aggregation Engine

Maintains rolling windows of sensor data and computes statistics:
- Moving averages
- Standard deviations
- Z-scores for anomaly detection
"""

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
import math


@dataclass
class AggregatedMetrics:
    """Statistics for a sensor over a time window."""
    sensor_id: str
    timestamp: str
    current_temp: float
    current_vibration: float
    avg_temp: float
    avg_vibration: float
    std_temp: float
    std_vibration: float
    z_score_temp: float
    z_score_vibration: float
    sample_count: int
    
    def to_dict(self):
        return {
            "sensor_id": self.sensor_id,
            "timestamp": self.timestamp,
            "current_temp": round(self.current_temp, 2),
            "current_vibration": round(self.current_vibration, 3),
            "avg_temp": round(self.avg_temp, 2),
            "avg_vibration": round(self.avg_vibration, 3),
            "std_temp": round(self.std_temp, 2),
            "std_vibration": round(self.std_vibration, 3),
            "z_score_temp": round(self.z_score_temp, 2),
            "z_score_vibration": round(self.z_score_vibration, 2),
            "sample_count": self.sample_count,
        }


class WindowedAggregator:
    """
    Maintains rolling windows of sensor readings and computes real-time statistics.
    """
    
    def __init__(self, window_size_seconds: int = 300):
        """
        Args:
            window_size_seconds: Size of rolling window (default: 5 minutes)
        """
        self.window_size = window_size_seconds
        self.windows: Dict[str, deque] = defaultdict(deque)
        self.metrics_cache: Dict[str, AggregatedMetrics] = {}
    
    def add_reading(self, sensor_id: str, temperature: float, 
                   vibration: float, timestamp: str) -> AggregatedMetrics:
        """
        Add a new reading to the window and compute aggregated metrics.
        
        Args:
            sensor_id: Sensor identifier
            temperature: Temperature reading (Fahrenheit)
            vibration: Vibration reading (g-force)
            timestamp: Timestamp string
            
        Returns:
            AggregatedMetrics with current statistics
        """
        # Add reading with current time (in real app, use actual timestamp)
        reading = {
            "temperature": temperature,
            "vibration": vibration,
            "timestamp": datetime.now(),
        }
        
        window = self.windows[sensor_id]
        window.append(reading)
        
        # Remove old readings outside the window
        cutoff_time = datetime.now()
        # Simplified: assume readings are ~1 second apart
        max_samples = max(1, int(self.window_size / 1.0))
        while len(window) > max_samples:
            window.popleft()
        
        # Compute metrics
        metrics = self._compute_metrics(sensor_id, temperature, vibration, timestamp)
        self.metrics_cache[sensor_id] = metrics
        
        return metrics
    
    def _compute_metrics(self, sensor_id: str, current_temp: float,
                        current_vibration: float, timestamp: str) -> AggregatedMetrics:
        """Compute moving average, std dev, and z-scores."""
        window = self.windows[sensor_id]
        
        if not window:
            return AggregatedMetrics(
                sensor_id=sensor_id,
                timestamp=timestamp,
                current_temp=current_temp,
                current_vibration=current_vibration,
                avg_temp=current_temp,
                avg_vibration=current_vibration,
                std_temp=0,
                std_vibration=0,
                z_score_temp=0,
                z_score_vibration=0,
                sample_count=0,
            )
        
        temps = [r["temperature"] for r in window]
        vibs = [r["vibration"] for r in window]
        
        # Compute mean
        avg_temp = sum(temps) / len(temps)
        avg_vib = sum(vibs) / len(vibs)
        
        # Compute standard deviation
        if len(temps) > 1:
            variance_temp = sum((t - avg_temp) ** 2 for t in temps) / len(temps)
            std_temp = math.sqrt(variance_temp)
        else:
            std_temp = 0
        
        if len(vibs) > 1:
            variance_vib = sum((v - avg_vib) ** 2 for v in vibs) / len(vibs)
            std_vib = math.sqrt(variance_vib)
        else:
            std_vib = 0
        
        # Compute z-scores (deviation from mean in units of std dev)
        z_score_temp = (current_temp - avg_temp) / std_temp if std_temp > 0 else 0
        z_score_vib = (current_vibration - avg_vib) / std_vib if std_vib > 0 else 0
        
        return AggregatedMetrics(
            sensor_id=sensor_id,
            timestamp=timestamp,
            current_temp=current_temp,
            current_vibration=current_vibration,
            avg_temp=avg_temp,
            avg_vibration=avg_vib,
            std_temp=std_temp,
            std_vibration=std_vib,
            z_score_temp=z_score_temp,
            z_score_vibration=z_score_vib,
            sample_count=len(window),
        )
    
    def get_metrics(self, sensor_id: str) -> Optional[AggregatedMetrics]:
        """Get cached metrics for a sensor."""
        return self.metrics_cache.get(sensor_id)


# Test
if __name__ == "__main__":
    agg = WindowedAggregator(window_size_seconds=60)
    
    # Simulate readings
    print("Testing aggregator with synthetic readings:\n")
    readings = [
        (70.0, 0.10), (71.5, 0.11), (72.0, 0.12), 
        (71.8, 0.13), (72.5, 0.12), (95.0, 0.35),  # Anomaly!
    ]
    
    for i, (temp, vib) in enumerate(readings):
        metrics = agg.add_reading(f"sensor-1", temp, vib, f"00:00:{i:02d}")
        print(f"Reading {i+1}: temp={temp}, vib={vib}")
        print(f"  → avg_temp={metrics.avg_temp:.1f}, std={metrics.std_temp:.2f}, "
              f"z_score={metrics.z_score_temp:.2f}")
        print(f"  → avg_vib={metrics.avg_vibration:.3f}, std={metrics.std_vibration:.3f}, "
              f"z_score={metrics.z_score_vibration:.2f}\n")
