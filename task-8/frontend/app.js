/**
 * Dashboard WebSocket Client
 *
 * Manages WebSocket connection, receives sensor data updates,
 * and renders live charts using Chart.js
 */

// WebSocket connection and state
let ws = null;
let isConnected = false;
const chartData = {
  temperature: [],
  vibration: [],
  zscoreTemp: [],
  zscoreVib: [],
  labels: [],
};
const maxDataPoints = 60; // Show last 60 seconds of data

// Chart instances
let tempChart = null;
let vibrationChart = null;
let zscoreChart = null;

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  console.log("Dashboard initialized, connecting to WebSocket...");
  initializeCharts();
  connectWebSocket();
  updateTime();
  setInterval(updateTime, 1000);
});

/**
 * Initialize Chart.js charts
 */
function initializeCharts() {
  // Chart.js configuration
  const chartConfig = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: true,
        position: "top",
      },
      filler: true,
    },
    scales: {
      y: {
        beginAtZero: false,
      },
      x: {
        display: true,
      },
    },
  };

  // Temperature Chart
  const tempCtx = document.getElementById("tempChart").getContext("2d");
  tempChart = new Chart(tempCtx, {
    type: "line",
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: "Temperature (°F)",
          data: chartData.temperature,
          borderColor: "#f59e0b",
          backgroundColor: "rgba(245, 158, 11, 0.1)",
          borderWidth: 2,
          fill: true,
          pointRadius: 2,
          pointBackgroundColor: "#f59e0b",
          tension: 0.4,
        },
        {
          label: "Threshold (100°F)",
          data: new Array(chartData.labels.length).fill(100),
          borderColor: "#ef4444",
          borderWidth: 2,
          borderDash: [5, 5],
          fill: false,
          pointRadius: 0,
        },
      ],
    },
    options: chartConfig,
  });

  // Vibration Chart
  const vibCtx = document.getElementById("vibrationChart").getContext("2d");
  vibrationChart = new Chart(vibCtx, {
    type: "line",
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: "Vibration (g)",
          data: chartData.vibration,
          borderColor: "#8b5cf6",
          backgroundColor: "rgba(139, 92, 246, 0.1)",
          borderWidth: 2,
          fill: true,
          pointRadius: 2,
          pointBackgroundColor: "#8b5cf6",
          tension: 0.4,
        },
        {
          label: "Threshold (0.50g)",
          data: new Array(chartData.labels.length).fill(0.5),
          borderColor: "#ef4444",
          borderWidth: 2,
          borderDash: [5, 5],
          fill: false,
          pointRadius: 0,
        },
      ],
    },
    options: chartConfig,
  });

  // Z-Score Chart
  const zscoreCtx = document.getElementById("zscoreChart").getContext("2d");
  zscoreChart = new Chart(zscoreCtx, {
    type: "line",
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: "Temperature Z-Score",
          data: chartData.zscoreTemp,
          borderColor: "#f59e0b",
          borderWidth: 2,
          fill: false,
          pointRadius: 2,
          pointBackgroundColor: "#f59e0b",
          tension: 0.4,
        },
        {
          label: "Vibration Z-Score",
          data: chartData.zscoreVib,
          borderColor: "#8b5cf6",
          borderWidth: 2,
          fill: false,
          pointRadius: 2,
          pointBackgroundColor: "#8b5cf6",
          tension: 0.4,
        },
        {
          label: "Anomaly Threshold",
          data: new Array(chartData.labels.length).fill(3.0),
          borderColor: "#ef4444",
          borderWidth: 1,
          borderDash: [5, 5],
          fill: false,
          pointRadius: 0,
        },
      ],
    },
    options: chartConfig,
  });
}

/**
 * Connect to WebSocket server
 */
function connectWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws`;

  ws = new WebSocket(wsUrl);

  ws.addEventListener("open", () => {
    console.log("WebSocket connected");
    updateConnectionStatus(true);
  });

  ws.addEventListener("message", (event) => {
    try {
      const message = JSON.parse(event.data);
      handleMessage(message);
    } catch (error) {
      console.error("Error parsing message:", error);
    }
  });

  ws.addEventListener("close", () => {
    console.log("WebSocket disconnected");
    updateConnectionStatus(false);
    // Attempt to reconnect after 3 seconds
    setTimeout(connectWebSocket, 3000);
  });

  ws.addEventListener("error", (error) => {
    console.error("WebSocket error:", error);
    updateConnectionStatus(false);
  });
}

/**
 * Handle incoming WebSocket messages
 */
function handleMessage(message) {
  switch (message.type) {
    case "initial_data":
      console.log("Received initial data");
      updateAllReadings(message.readings);
      break;
    case "sensor_update":
      updateAllReadings(message.readings);
      break;
    case "alert":
      handleAlert(message.alert);
      break;
    default:
      console.warn("Unknown message type:", message.type);
  }
}

/**
 * Update all sensor readings and charts
 */
function updateAllReadings(readings) {
  const timestamp = new Date().toLocaleTimeString();

  // Update chart data
  if (chartData.labels.length >= maxDataPoints) {
    chartData.labels.shift();
    chartData.temperature.shift();
    chartData.vibration.shift();
    chartData.zscoreTemp.shift();
    chartData.zscoreVib.shift();
  }

  chartData.labels.push(timestamp.substring(0, 8));

  let avgTemp = 0,
    avgVib = 0,
    avgZTemp = 0,
    avgZVib = 0;
  let tempCounter = 0,
    vibCounter = 0;

  // Update sensor status and aggregate data
  const sensorList = document.getElementById("sensor-list");
  sensorList.innerHTML = "";

  for (const [sensorId, data] of Object.entries(readings)) {
    const reading = data.reading;
    const metrics = data.metrics;

    // Determine status
    let status = "normal";
    if (reading.temperature > 100 || reading.vibration > 0.5) {
      status = "critical";
    } else if (
      Math.abs(metrics.z_score_temp) > 2 ||
      Math.abs(metrics.z_score_vibration) > 2
    ) {
      status = "warning";
    }

    // Create sensor item
    const sensorItem = document.createElement("div");
    sensorItem.className = `sensor-item ${status}`;
    sensorItem.innerHTML = `
            <div class="sensor-status-indicator"></div>
            <div class="sensor-info">
                <div class="sensor-name">${sensorId}</div>
                <div class="sensor-values">
                    Temp: ${reading.temperature.toFixed(1)}°F (avg: ${metrics.avg_temp.toFixed(1)}°F) |
                    Vib: ${reading.vibration.toFixed(3)}g (avg: ${metrics.avg_vibration.toFixed(3)}g)
                </div>
            </div>
        `;
    sensorList.appendChild(sensorItem);

    // Aggregate for main display
    avgTemp += reading.temperature;
    avgVib += reading.vibration;
    avgZTemp += metrics.z_score_temp;
    avgZVib += metrics.z_score_vibration;
    tempCounter++;
    vibCounter++;

    // Update main stats on first sensor
    if (
      sensorId === "sensor-T1" ||
      Object.keys(readings).indexOf(sensorId) === 0
    ) {
      document.getElementById("current-temp").textContent =
        reading.temperature.toFixed(1);
      document.getElementById("avg-temp").textContent =
        metrics.avg_temp.toFixed(1);
      document.getElementById("current-vib").textContent =
        reading.vibration.toFixed(3);
      document.getElementById("avg-vib").textContent =
        metrics.avg_vibration.toFixed(3);
      document.getElementById("zscore-temp").textContent =
        metrics.z_score_temp.toFixed(2);
      document.getElementById("zscore-vib").textContent =
        metrics.z_score_vibration.toFixed(2);
    }
  }

  // Add aggregated data to charts
  if (tempCounter > 0) {
    chartData.temperature.push(avgTemp / tempCounter);
    chartData.vibration.push(avgVib / vibCounter);
    chartData.zscoreTemp.push(avgZTemp / tempCounter);
    chartData.zscoreVib.push(avgZVib / vibCounter);
  }

  // Update charts
  updateCharts();
}

/**
 * Handle alert messages
 */
function handleAlert(alert) {
  const container = document.getElementById("alerts-container");

  // Remove "no alerts" message
  const noAlertsMsg = container.querySelector(".no-alerts");
  if (noAlertsMsg) {
    noAlertsMsg.remove();
  }

  // Create alert element
  const alertItem = document.createElement("div");
  alertItem.className = `alert-item ${alert.severity.toLowerCase()}`;

  const timeStr = alert.timestamp;
  const valueStr =
    alert.metric_type === "temperature"
      ? `${alert.current_value.toFixed(1)}°F`
      : `${alert.current_value.toFixed(3)}g`;

  let detailText = "";
  if (alert.z_score) {
    detailText = ` | Z-score: ${alert.z_score.toFixed(2)}`;
  }

  alertItem.innerHTML = `
        <strong>${alert.sensor_id}</strong> [${timeStr}] ${alert.message}
        <br>
        <small>Value: ${valueStr} | Threshold: ${alert.threshold_value.toFixed(1)}${detailText}</small>
    `;

  container.insertBefore(alertItem, container.firstChild);

  // Keep only last 20 alerts
  while (container.children.length > 20) {
    container.removeChild(container.lastChild);
  }

  // Auto-fade out after 10 seconds
  setTimeout(() => {
    alertItem.style.opacity = "0.5";
  }, 10000);
}

/**
 * Update all charts with new data
 */
function updateCharts() {
  if (tempChart) {
    tempChart.data.labels = chartData.labels;
    tempChart.data.datasets[0].data = chartData.temperature;
    tempChart.data.datasets[1].data = new Array(chartData.labels.length).fill(
      100,
    );
    tempChart.update("none");
  }

  if (vibrationChart) {
    vibrationChart.data.labels = chartData.labels;
    vibrationChart.data.datasets[0].data = chartData.vibration;
    vibrationChart.data.datasets[1].data = new Array(
      chartData.labels.length,
    ).fill(0.5);
    vibrationChart.update("none");
  }

  if (zscoreChart) {
    zscoreChart.data.labels = chartData.labels;
    zscoreChart.data.datasets[0].data = chartData.zscoreTemp;
    zscoreChart.data.datasets[1].data = chartData.zscoreVib;
    zscoreChart.data.datasets[2].data = new Array(chartData.labels.length).fill(
      3.0,
    );
    zscoreChart.update("none");
  }
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(connected) {
  isConnected = connected;
  const statusEl = document.getElementById("connection-status");
  if (connected) {
    statusEl.textContent = "● Connected";
    statusEl.className = "status connected";
  } else {
    statusEl.textContent = "● Disconnected";
    statusEl.className = "status disconnected";
  }
}

/**
 * Update current time display
 */
function updateTime() {
  const now = new Date();
  document.getElementById("current-time").textContent =
    now.toLocaleTimeString();
}
