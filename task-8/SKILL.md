# Skill: Task 8 - Real-Time Data Streaming Dashboard

This skill provides comprehensive guidance for developing and debugging the real-time data streaming dashboard.

## Overview

Task 8 implements a live data streaming system using FastAPI WebSockets. It simulates IoT sensors, performs windowed aggregations (5-minute moving averages), detects anomalies via z-scores, and pushes real-time updates to browser clients with Chart.js visualization.

## Project Architecture

### Components

1. **server.py**: FastAPI application with WebSocket endpoints and lifecycle management
2. **sensor_simulator.py**: Generates realistic temperature/vibration data with controlled anomalies
3. **aggregator.py**: Maintains rolling windows, computes moving averages, z-score detection
4. **alert_system.py**: Threshold-based alert triggering and management
5. **frontend/**: HTML/CSS/JavaScript dashboard with WebSocket client and Chart.js

## Common Tasks & Solutions

### Starting the Server

```bash
cd task-8
python server.py
```

Server runs on `http://localhost:8000` with dashboard at `/dashboard`.

### Understanding Data Flow

1. `sensor_simulator.py` generates data points continuously
2. `aggregator.py` processes incoming data in 5-minute windows
3. `alert_system.py` monitors thresholds and creates alert events
4. `server.py` broadcasts aggregated data + alerts to connected WebSocket clients
5. `frontend/app.js` receives updates and re-renders charts in real-time

### Debugging WebSocket Issues

**Problem**: Client can't connect to WebSocket

- Check server is running on correct port (8000 by default)
- Verify CORS settings in FastAPI app
- Check browser console for WebSocket URL mismatch
- Ensure `/ws` endpoint is correctly implemented

**Problem**: Data not updating in real-time

- Check if sensor simulator is running (should log data generation)
- Verify aggregator is processing windows on schedule
- Check browser network tab for WebSocket frames
- Verify data is being broadcast correctly in `server.py`

### Performance Optimization

- **Reduce data transmission**: Aggregate data at server before broadcasting
- **Optimize window size**: Smaller windows = more frequent updates but more CPU
- **Batch WebSocket messages**: Send multiple data points in single message
- **Frontend optimization**: Use requestAnimationFrame for chart updates

## Common Deprecation Warning

FastAPI 0.104.1 shows deprecation warnings for `@app.on_event()`. This is not critical but can be fixed by migrating to lifespan context managers:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    # startup code
    yield
    # shutdown code

app = FastAPI(lifespan=lifespan)
```

## Key Files to Understand

- `server.py` lines 1-50: FastAPI setup and WebSocket handler
- `aggregator.py`: Window management and statistics calculation
- `frontend/app.js`: Chart.js integration and real-time updates

## Testing Locally

Open browser to `http://localhost:8000/dashboard` while server is running. You should see:

- Real-time line charts updating every second
- Temperature and vibration readings
- Alert notifications when thresholds exceeded
