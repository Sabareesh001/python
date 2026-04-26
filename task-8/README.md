# Task 8: Real-Time Data Streaming Dashboard

A live data streaming application that consumes IoT sensor data, applies windowed aggregations (moving averages, anomaly detection), and pushes updates to a browser dashboard via WebSockets.

## Features

- **Real-time Sensor Simulation**: Simulates IoT sensors with temperature and vibration data
- **Windowed Aggregations**: Computes 5-minute moving averages and z-score anomaly detection
- **WebSocket Integration**: Pushes live updates to connected browser clients every second
- **Alert System**: Triggers alerts when readings exceed configurable thresholds
- **Live Dashboard**: Interactive HTML/CSS/JavaScript frontend with Chart.js visualization
- **Scalable Architecture**: Event-driven design supports multiple concurrent clients

## Project Structure

```
task-8/
├── README.md
├── requirements.txt
├── server.py              # FastAPI WebSocket server
├── sensor_simulator.py    # Simulates IoT sensor data streams
├── aggregator.py          # Windowed aggregations and anomaly detection
├── alert_system.py        # Alert triggering and management
└── frontend/
    ├── index.html         # Dashboard UI
    ├── styles.css         # Dashboard styling
    └── app.js             # Frontend WebSocket client and charting
```

## How It Works

1. **Sensor Simulation**: `sensor_simulator.py` generates realistic temperature and vibration readings with anomalies
2. **Aggregation**: `aggregator.py` maintains a 5-minute rolling window and computes statistics (mean, std dev, z-score)
3. **Alert Detection**: `alert_system.py` monitors thresholds and triggers alerts when anomalies are detected
4. **Real-time Push**: `server.py` broadcasts aggregated data and alerts to all connected WebSocket clients
5. **Frontend Visualization**: `frontend/app.js` receives updates and renders live-updating line charts

## Running the Application

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the server

```bash
python server.py
```

Expected output:

```
[INFO] Stream processor started — consuming from sensors/factory-a
[INFO] Dashboard available at http://localhost:8000/dashboard
[INFO] Uvicorn running on http://127.0.0.1:8000
```

### 3. Open the dashboard

Open `http://localhost:8000/dashboard` in your web browser.

### 4. Monitor console output

The console shows real-time sensor readings, moving averages, and alert triggers.

## Example Output

```
=== Live Sensor Feed (every 1s) ===
[14:05:31] sensor-T1  temp=72.3F  vibration=0.12g  status=NORMAL
[14:05:32] sensor-T1  temp=73.1F  vibration=0.14g  status=NORMAL
[14:05:33] sensor-T1  temp=89.7F  vibration=0.31g  status=WARNING
[14:05:34] sensor-T1  temp=104.2F vibration=0.58g  status=CRITICAL

=== Alert Triggered ===
[ALERT] sensor-T1 — Temperature exceeded threshold (>100F)
        Current: 104.2F | 5-min avg: 82.4F | Deviation: +2.7 sigma
        Action: Notification sent to ops-team@factory.com
```

## Architecture Patterns

- **Async Generators**: `sensor_simulator.py` uses async generators to emit data continuously
- **Event-Driven Design**: Alert system publishes events that server broadcasts to clients
- **Windowed Aggregation**: Pandas rolling windows compute moving averages efficiently
- **Statistical Analysis**: Z-scores detect anomalies relative to baseline

## Customization

- **Thresholds**: Edit `TEMP_THRESHOLD` and `VIBRATION_THRESHOLD` in `server.py`
- **Window Size**: Change `WINDOW_SIZE_SECONDS` in `aggregator.py` (default: 300s / 5 min)
- **Sensor Count**: Modify `NUM_SENSORS` in `sensor_simulator.py`
- **Update Frequency**: Adjust `BROADCAST_INTERVAL_SECONDS` in `server.py`

## Learning Outcomes

- ✅ Async generators and `asyncio` streams
- ✅ FastAPI WebSocket implementation
- ✅ Pandas windowed aggregations (rolling windows)
- ✅ Statistical anomaly detection (z-scores)
- ✅ Real-time data visualization with Chart.js
- ✅ Event-driven architecture patterns
