"""
IoT Sensor Data Simulator

Simulates a stream of sensor readings with realistic variations and occasional anomalies.
"""

import asyncio
import random
from datetime import datetime
from dataclasses import dataclass
from typing import AsyncGenerator


@dataclass
class SensorReading:
    """Represents a single sensor reading."""
    sensor_id: str
    timestamp: str
    temperature: float  # Fahrenheit
    vibration: float    # g-force
    
    def to_dict(self):
        return {
            "sensor_id": self.sensor_id,
            "timestamp": self.timestamp,
            "temperature": round(self.temperature, 2),
            "vibration": round(self.vibration, 3),
        }


class SensorSimulator:
    """Simulates multiple IoT sensors with realistic data and anomalies."""
    
    def __init__(self, num_sensors: int = 3):
        self.num_sensors = num_sensors
        self.sensor_ids = [f"sensor-T{i+1}" for i in range(num_sensors)]
        # Base temperatures and vibrations for each sensor
        self.base_temps = {sid: 70 + random.uniform(-5, 5) for sid in self.sensor_ids}
        self.base_vibrations = {sid: 0.1 + random.uniform(-0.02, 0.02) for sid in self.sensor_ids}
        self.anomaly_counters = {sid: 0 for sid in self.sensor_ids}
        self.anomaly_probability = 0.15  # 15% chance of anomaly per reading
        
    async def stream(self, interval: float = 1.0) -> AsyncGenerator[SensorReading, None]:
        """
        Generate a continuous stream of sensor readings.
        
        Args:
            interval: Time between readings in seconds
            
        Yields:
            SensorReading objects at regular intervals
        """
        while True:
            for sensor_id in self.sensor_ids:
                reading = self._generate_reading(sensor_id)
                yield reading
            await asyncio.sleep(interval)
    
    def _generate_reading(self, sensor_id: str) -> SensorReading:
        """Generate a single sensor reading with optional anomalies."""
        # Normal variation
        temp_variation = random.gauss(0, 2)  # Normal distribution, std dev = 2F
        vibration_variation = random.gauss(0, 0.02)
        
        # Occasionally inject anomalies
        if random.random() < self.anomaly_probability:
            self.anomaly_counters[sensor_id] += 1
            # Strong spike anomaly
            if self.anomaly_counters[sensor_id] % 5 == 0:
                temp_variation += random.uniform(15, 35)  # Large spike
                vibration_variation += random.uniform(0.3, 0.6)
            # Sustained elevation
            elif self.anomaly_counters[sensor_id] % 3 == 0:
                temp_variation += random.uniform(8, 15)
                vibration_variation += random.uniform(0.15, 0.25)
        
        temperature = self.base_temps[sensor_id] + temp_variation
        vibration = max(0, self.base_vibrations[sensor_id] + vibration_variation)
        
        # Clamp to reasonable ranges
        temperature = max(50, min(150, temperature))
        vibration = min(2.0, vibration)
        
        return SensorReading(
            sensor_id=sensor_id,
            timestamp=datetime.now().strftime("%H:%M:%S"),
            temperature=temperature,
            vibration=vibration,
        )
    
    def reset_baseline(self):
        """Recalibrate baseline values (simulates sensor warmup/reset)."""
        for sid in self.sensor_ids:
            self.base_temps[sid] = 70 + random.uniform(-5, 5)
            self.base_vibrations[sid] = 0.1 + random.uniform(-0.02, 0.02)


# Simple test
if __name__ == "__main__":
    async def main():
        simulator = SensorSimulator(num_sensors=2)
        
        print("Simulating sensor data (first 10 readings)...\n")
        count = 0
        async for reading in simulator.stream(interval=0.5):
            print(f"[{reading.timestamp}] {reading.sensor_id:12} "
                  f"temp={reading.temperature:6.1f}F  "
                  f"vibration={reading.vibration:6.3f}g")
            count += 1
            if count >= 10:
                break
    
    asyncio.run(main())
