import { useEffect, useState } from "react";

const API = "http://localhost:5000";

function Dashboard() {
  const [status, setStatus] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [incidents, setIncidents] = useState([]);

  const loadData = async () => {
    try {
      const [
        statusResponse,
        statisticsResponse,
        incidentsResponse
      ] = await Promise.all([
        fetch(`${API}/api/status`, {
          cache: "no-store"
        }),

        fetch(`${API}/api/statistics`, {
          cache: "no-store"
        }),

        fetch(`${API}/api/incidents`, {
          cache: "no-store"
        })
      ]);

      if (!statusResponse.ok) {
        throw new Error("Status request failed");
      }

      if (!statisticsResponse.ok) {
        throw new Error("Statistics request failed");
      }

      if (!incidentsResponse.ok) {
        throw new Error("Incidents request failed");
      }

      setStatus(await statusResponse.json());
      setStatistics(await statisticsResponse.json());
      setIncidents(await incidentsResponse.json());

    } catch (error) {
      console.error("Dashboard error:", error);
    }
  };

  useEffect(() => {
    loadData();

    const interval = setInterval(loadData, 1000);

    return () => clearInterval(interval);
  }, []);

  const drowning = status?.label === "DROWNING";

  const emergencyActive =
    Boolean(status?.incident_active);

  const alarmOn =
    status?.alarm === "ON";

  const iotConnected =
    status?.iot === "CONNECTED";

  return (
    <div className="page">

      {/* HEADER */}
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>

          <p>
            AquaGuard real-time pool safety monitoring
          </p>
        </div>
      </div>


      {/* MAIN STATISTICS */}
      <div className="stats-grid">

        <div className="stat-card">
          <span>Current Status</span>

          <strong
            className={
              drowning
                ? "text-danger"
                : "text-success"
            }
          >
            {status?.label || "WAITING"}
          </strong>
        </div>


        <div className="stat-card">
          <span>Confidence</span>

          <strong>
            {status?.confidence_percent ?? 0}%
          </strong>
        </div>


        <div className="stat-card">
          <span>Total Predictions</span>

          <strong>
            {statistics?.total_predictions ?? 0}
          </strong>
        </div>


        <div className="stat-card">
          <span>Incidents</span>

          <strong>
            {incidents.length}
          </strong>
        </div>

      </div>


      {/* MONITORING */}
      <div className="monitoring-grid">

        {/* VIDEO */}
        <div className="card video-card">

          <div className="card-header">

            <div>
              <h2>Live Monitoring</h2>

              <p>
                CNN-powered pool analysis
              </p>
            </div>

            <span
              className={
                status?.running
                  ? "status-badge status-safe"
                  : "status-badge status-warning"
              }
            >
              {status?.running
                ? "Monitoring"
                : "Stopped"}
            </span>

          </div>


          <div className="video-container">

            {status?.running ? (

              <img
                src={`${API}/video`}
                alt="Pool monitoring"
                className="live-video"
              />

            ) : (

              <div className="video-placeholder">

                <strong>
                  Monitoring is stopped
                </strong>

                <p>
                  Start monitoring from Live Monitoring.
                </p>

              </div>

            )}

          </div>

        </div>


        {/* AI PREDICTION */}
        <div className="card">

          <div className="card-header">

            <div>
              <h2>AI Prediction</h2>

              <p>
                Current model prediction
              </p>
            </div>

          </div>


          <div
            className={
              drowning
                ? "prediction-status prediction-danger"
                : "prediction-status prediction-safe"
            }
          >

            <span className="prediction-label">
              {status?.label || "WAITING"}
            </span>

            <span className="prediction-confidence">
              {status?.confidence_percent ?? 0}%
            </span>

          </div>


          <div className="prediction-details">

            {/* FPS */}
            <div className="detail-row">
              <span>FPS</span>

              <strong>
                {status?.fps ?? 0}
              </strong>
            </div>


            {/* INFERENCE */}
            <div className="detail-row">
              <span>Inference</span>

              <strong>
                {status?.inference_ms ?? 0} ms
              </strong>
            </div>


            {/* ALARM */}
            <div className="detail-row">
              <span>Alarm</span>

              <strong
                className={
                  alarmOn
                    ? "text-danger"
                    : "text-success"
                }
              >
                {status?.alarm || "OFF"}
              </strong>
            </div>


            {/* IOT */}
            <div className="detail-row">
              <span>IoT</span>

              <strong
                className={
                  iotConnected
                    ? "text-success"
                    : "text-warning"
                }
              >
                {status?.iot || "DISCONNECTED"}
              </strong>
            </div>


            {/* BUZZER */}
            <div className="detail-row">
              <span>Buzzer</span>

              <strong
                className={
                  alarmOn
                    ? "text-danger"
                    : "text-success"
                }
              >
                {alarmOn ? "ON" : "OFF"}
              </strong>
            </div>


            {/* SERVO */}
            <div className="detail-row">
              <span>Servo</span>

              <strong>
                {status?.servo_angle ?? 0}°
              </strong>
            </div>


            {/* EMERGENCY */}
            <div className="detail-row">
              <span>Emergency</span>

              <strong
                className={
                  emergencyActive
                    ? "text-danger"
                    : "text-success"
                }
              >
                {emergencyActive
                  ? "ACTIVE"
                  : "NORMAL"}
              </strong>
            </div>

          </div>

        </div>

      </div>


      {/* INCIDENTS */}
      <div className="card">

        <div className="card-header">

          <div>
            <h2>Recent Incidents</h2>

            <p>
              Confirmed drowning events
            </p>
          </div>

        </div>


        {incidents.length === 0 ? (

          <div className="empty-state">
            No incidents recorded yet.
          </div>

        ) : (

          incidents
            .slice(0, 5)
            .map((incident) => (

              <div
                className="detail-row"
                key={incident.id}
              >

                <span>
                  Incident #{incident.id}
                </span>

                <strong>
                  {incident.confidence}%
                </strong>

              </div>

            ))

        )}

      </div>

    </div>
  );
}

export default Dashboard;