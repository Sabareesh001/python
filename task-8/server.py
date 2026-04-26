"""
FastAPI Server with WebSocket Support for Real-Time Dashboard

Serves the dashboard UI and manages WebSocket connections for live sensor data streaming.
"""

import asyncio
import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from sensor_simulator import SensorSimulator
from aggregator import WindowedAggregator
from alert_system import AlertSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
NUM_SENSORS = 3
WINDOW_SIZE_SECONDS = 300  # 5 minutes
BROADCAST_INTERVAL_SECONDS = 1
SENSOR_READ_INTERVAL = 1.0
TEMP_THRESHOLD = 100.0
VIB_THRESHOLD = 0.5
Z_SCORE_THRESHOLD = 3.0

# Application state
app = FastAPI(title="Sensor Dashboard")
simulator = SensorSimulator(num_sensors=NUM_SENSORS)
aggregator = WindowedAggregator(window_size_seconds=WINDOW_SIZE_SECONDS)
alert_system = AlertSystem()

# Connected WebSocket clients
connected_clients = set()

# Shared state for current readings
current_readings = {}


async def broadcast_to_clients(message: dict):
    """Broadcast a message to all connected WebSocket clients."""
    if not connected_clients:
        return
    
    json_message = json.dumps(message)
    disconnected = set()
    
    for client in connected_clients:
        try:
            await client.send_text(json_message)
        except Exception as e:
            logger.warning(f"Error sending to client: {e}")
            disconnected.add(client)
    
    # Remove disconnected clients
    for client in disconnected:
        connected_clients.discard(client)


async def sensor_data_task():
    """
    Main task: reads sensor data, computes aggregations, checks alerts,
    and broadcasts updates to clients.
    """
    logger.info(f"Stream processor started — consuming from sensors/factory-a")
    
    # Start sensor stream
    reading_task = asyncio.create_task(simulator.stream(interval=SENSOR_READ_INTERVAL))
    last_broadcast = asyncio.get_event_loop().time()
    
    try:
        async for reading in reading_task:
            # Add to aggregator and get metrics
            metrics = aggregator.add_reading(
                reading.sensor_id,
                reading.temperature,
                reading.vibration,
                reading.timestamp
            )
            
            # Store current reading
            current_readings[reading.sensor_id] = {
                "reading": reading.to_dict(),
                "metrics": metrics.to_dict(),
            }
            
            # Check for alerts
            alert = alert_system.check_thresholds(
                reading.sensor_id,
                reading.temperature,
                reading.vibration,
                metrics.avg_temp,
                metrics.avg_vibration,
                metrics.z_score_temp,
                metrics.z_score_vibration,
                temp_threshold=TEMP_THRESHOLD,
                vib_threshold=VIB_THRESHOLD,
                z_score_threshold=Z_SCORE_THRESHOLD,
            )
            
            # Broadcast updates at regular interval
            now = asyncio.get_event_loop().time()
            if now - last_broadcast >= BROADCAST_INTERVAL_SECONDS:
                message = {
                    "type": "sensor_update",
                    "readings": current_readings,
                    "timestamp": reading.timestamp,
                }
                await broadcast_to_clients(message)
                last_broadcast = now
                
                # Console output with status
                status = "NORMAL"
                if reading.temperature > TEMP_THRESHOLD or reading.vibration > VIB_THRESHOLD:
                    status = "CRITICAL"
                elif abs(metrics.z_score_temp) > 2 or abs(metrics.z_score_vibration) > 2:
                    status = "WARNING"
                
                print(f"[{reading.timestamp}] {reading.sensor_id:12} "
                      f"temp={reading.temperature:6.1f}F  "
                      f"vibration={reading.vibration:6.3f}g  "
                      f"status={status:8}")
            
            if alert:
                # Broadcast alert
                alert_msg = {
                    "type": "alert",
                    "alert": alert.to_dict(),
                }
                await broadcast_to_clients(alert_msg)
    
    except asyncio.CancelledError:
        logger.info("Sensor data task cancelled")
    except Exception as e:
        logger.error(f"Error in sensor data task: {e}", exc_info=True)


# Global task reference
sensor_task = None


@app.on_event("startup")
async def startup_event():
    """Start the sensor data processing task on server startup."""
    global sensor_task
    sensor_task = asyncio.create_task(sensor_data_task())
    logger.info(f"Dashboard available at http://localhost:8000/dashboard")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on server shutdown."""
    global sensor_task
    if sensor_task:
        sensor_task.cancel()
        try:
            await sensor_task
        except asyncio.CancelledError:
            pass


@app.get("/dashboard")
async def dashboard():
    """Serve the dashboard HTML."""
    return FileResponse("frontend/index.html", media_type="text/html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for client connections."""
    await websocket.accept()
    connected_clients.add(websocket)
    logger.info(f"Client connected. Total: {len(connected_clients)}")
    
    try:
        # Send initial data
        if current_readings:
            message = {
                "type": "initial_data",
                "readings": current_readings,
            }
            await websocket.send_text(json.dumps(message))
        
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            # Echo back or process commands if needed
            logger.debug(f"Received: {data}")
    
    except WebSocketDisconnect:
        connected_clients.discard(websocket)
        logger.info(f"Client disconnected. Total: {len(connected_clients)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        connected_clients.discard(websocket)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "connected_clients": len(connected_clients),
        "sensors": len(current_readings),
    }


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
