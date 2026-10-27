import { useEffect, useState } from "react";

const API_BASE = "http://localhost:5000";

function LiveMonitoring() {

  const [status, setStatus] = useState(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [streamKey, setStreamKey] = useState(0);


  // =====================================================
  // GET BACKEND STATUS
  // =====================================================

  const fetchStatus = async () => {

    try {

      const response =
        await fetch(
          `${API_BASE}/api/status`,
          {
            cache: "no-store"
          }
        );

      if (!response.ok) {

        throw new Error(
          "Backend status request failed."
        );
      }

      const data =
        await response.json();

      setStatus(data);

      setError("");

    } catch (error) {

      console.error(
        "Status error:",
        error
      );

      setError(
        "Backend is not connected. Make sure python app.py is running."
      );
    }
  };


  // =====================================================
  // POLLING
  // =====================================================

  useEffect(() => {

    fetchStatus();

    const interval =
      setInterval(
        fetchStatus,
        1000
      );

    return () => {

      clearInterval(interval);

    };

  }, []);


  // =====================================================
  // START
  // =====================================================

  const startMonitoring = async () => {

    if (loading) {

      return;
    }

    setLoading(true);

    setError("");

    try {

      const response =
        await fetch(
          `${API_BASE}/api/monitoring/start`,
          {
            method: "POST"
          }
        );

      const data =
        await response.json();

      console.log(
        "Start response:",
        data
      );

      if (!response.ok || !data.success) {

        throw new Error(
          data.message ||
          "Monitoring could not be started."
        );
      }

      // Give backend a moment to open video
      await new Promise(
        resolve =>
          setTimeout(
            resolve,
            500
          )
      );

      await fetchStatus();

      // Force browser to create a fresh stream
      setStreamKey(
        previous =>
          previous + 1
      );

    } catch (error) {

      console.error(
        "Start monitoring error:",
        error
      );

      setError(
        error.message ||
        "Unable to start monitoring."
      );

    } finally {

      setLoading(false);
    }
  };


  // =====================================================
  // STOP
  // =====================================================

  const stopMonitoring = async () => {

    if (loading) {

      return;
    }

    setLoading(true);

    setError("");

    try {

      const response =
        await fetch(
          `${API_BASE}/api/monitoring/stop`,
          {
            method: "POST"
          }
        );

      const data =
        await response.json();

      if (!response.ok || !data.success) {

        throw new Error(
          data.message ||
          "Monitoring could not be stopped."
        );
      }

      await fetchStatus();

    } catch (error) {

      console.error(
        "Stop monitoring error:",
        error
      );

      setError(
        error.message ||
        "Unable to stop monitoring."
      );

    } finally {

      setLoading(false);
    }
  };


  // =====================================================
  // RESET EMERGENCY
  // =====================================================

  const resetEmergency = async () => {

    try {

      const response =
        await fetch(
          `${API_BASE}/api/emergency/reset`,
          {
            method: "POST"
          }
        );

      const data =
        await response.json();

      if (!response.ok || !data.success) {

        throw new Error(
          data.message ||
          "Unable to reset emergency."
        );
      }

      await fetchStatus();

    } catch (error) {

      console.error(
        "Emergency reset error:",
        error
      );

      setError(
        error.message ||
        "Unable to reset emergency."
      );
    }
  };


  // =====================================================
  // VALUES
  // =====================================================

  const monitoring =
    Boolean(
      status?.running
    );

  const prediction =
    status?.label ||
    "WAITING";

  const confidence =
    status?.confidence_percent ??
    0;

  const isDrowning =
    prediction === "DROWNING";

  const emergencyActive =
    Boolean(
      status?.incident_active
    );

  const alarmOn =
    status?.alarm === "ON";


  // =====================================================
  // UI
  // =====================================================

  return (

    <div className="page live-monitoring-page">

      {/* HEADER */}

      <div className="page-header">

        <div>

          <h1>
            Live Monitoring
          </h1>

          <p>
            Real-time swimming pool safety
            monitoring using the AquaGuard CNN model.
          </p>

        </div>


        <div className="page-actions">

          {!monitoring ? (

            <button
              className="btn btn-primary"
              onClick={
                startMonitoring
              }
              disabled={loading}
            >

              {loading
                ? "Starting..."
                : "Start Monitoring"}

            </button>

          ) : (

            <button
              className="btn btn-danger"
              onClick={
                stopMonitoring
              }
              disabled={loading}
            >

              {loading
                ? "Stopping..."
                : "Stop Monitoring"}

            </button>

          )}

        </div>

      </div>


      {/* CONNECTION ERROR */}

      {error && (

        <div className="system-error">

          <strong>
            System
          </strong>

          <span>
            {error}
          </span>

        </div>

      )}


      {/* EMERGENCY */}

      {emergencyActive && (

        <div className="emergency-banner">

          <div className="emergency-banner-content">

            <div>

              <strong>
                DROWNING EMERGENCY DETECTED
              </strong>

              <p>
                The CNN has confirmed an
                emergency condition.
              </p>

            </div>


            <button
              className="btn btn-light"
              onClick={
                resetEmergency
              }
            >
              Reset Emergency
            </button>

          </div>

        </div>

      )}


      {/* MAIN GRID */}

      <div className="monitoring-grid">


        {/* VIDEO */}

        <div className="card video-card">

          <div className="card-header">

            <div>

              <h2>
                Live Pool Camera
              </h2>

              <p>
                Real-time video analysis
              </p>

            </div>


            <span
              className={
                monitoring
                  ? "status-badge status-safe"
                  : "status-badge status-warning"
              }
            >

              <span className="status-badge-dot"></span>

              {monitoring
                ? "Monitoring"
                : "Stopped"}

            </span>

          </div>


          <div className="video-container">

            {monitoring ? (

              <img
                key={streamKey}
                src={`${API_BASE}/video?stream=${streamKey}`}
                alt="AquaGuard live pool monitoring"
                className="live-video"
              />

            ) : (

              <div className="video-placeholder">

                <div className="video-placeholder-content">

                  <div className="video-placeholder-icon">
                    VIDEO
                  </div>

                  <strong>
                    Monitoring is stopped
                  </strong>

                  <p>
                    Click "Start Monitoring"
                    to start the CNN analysis.
                  </p>

                </div>

              </div>

            )}

          </div>

        </div>


        {/* AI PREDICTION */}

        <div className="card prediction-card">

          <div className="card-header">

            <div>

              <h2>
                AI Prediction
              </h2>

              <p>
                Current CNN analysis
              </p>

            </div>

          </div>


          <div
            className={
              isDrowning
                ? "prediction-status prediction-danger"
                : "prediction-status prediction-safe"
            }
          >

            <div>

              <span className="prediction-heading">
                Current Detection
              </span>

              <span className="prediction-label">
                {prediction}
              </span>

            </div>


            <span className="prediction-confidence">

              {confidence}%

            </span>

          </div>


          {/* CONFIDENCE */}

          <div className="confidence-section">

            <div className="confidence-header">

              <span>
                Confidence
              </span>

              <strong>
                {confidence}%
              </strong>

            </div>


            <div className="confidence-bar">

              <div
                className={
                  isDrowning
                    ? "confidence-fill confidence-danger"
                    : "confidence-fill"
                }
                style={{
                  width:
                    `${Math.min(
                      Math.max(
                        confidence,
                        0
                      ),
                      100
                    )}%`
                }}
              ></div>

            </div>

          </div>


          {/* DETAILS */}

          <div className="prediction-details">

            <div className="detail-row">

              <span>
                Detection FPS
              </span>

              <strong>
                {status?.fps ?? 0}
              </strong>

            </div>


            <div className="detail-row">

              <span>
                Inference Time
              </span>

              <strong>
                {status?.inference_ms ?? 0}
                {" "}ms
              </strong>

            </div>


            <div className="detail-row">

              <span>
                Consecutive Drowning
              </span>

              <strong
                className={
                  status?.consecutive_drowning > 0
                    ? "text-danger"
                    : "text-success"
                }
              >
                {status?.consecutive_drowning ?? 0}
              </strong>

            </div>


            <div className="detail-row">

              <span>
                Alarm
              </span>

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


            <div className="detail-row">

              <span>
                Emergency
              </span>

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


            <div className="detail-row">

              <span>
                IoT Device
              </span>

              <strong
                className={
                  status?.iot === "CONNECTED"
                    ? "text-success"
                    : "text-warning"
                }
              >
                {status?.iot ||
                  "DISCONNECTED"}
              </strong>

            </div>
            <div className="detail-row">

              <span>
                Buzzer
              </span>

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


              <div className="detail-row">

                <span>
                  Rescue Servo
                </span>

                <strong>
                {status?.servo_angle ?? 0}°
                </strong>

            </div>

            <div className="detail-row">

              <span>
                SMS
              </span>

              <strong>
                {status?.sms ||
                  "READY"}
              </strong>

            </div>

          </div>

        </div>

      </div>


      {/* STATISTICS */}

      <div className="section-heading">

        <div>

          <h2>
            Live Statistics
          </h2>

          <p>
            Values generated from the CNN
            prediction engine.
          </p>

        </div>

      </div>


      <div className="stats-grid">

        <div className="stat-card">

          <span>
            Total Predictions
          </span>

          <strong>
            {status?.total_predictions ?? 0}
          </strong>

        </div>


        <div className="stat-card">

          <span>
            Drowning Predictions
          </span>

          <strong className="text-danger">
            {status?.total_drowning ?? 0}
          </strong>

        </div>


        <div className="stat-card">

          <span>
            Safe Predictions
          </span>

          <strong className="text-success">
            {status?.total_safe ?? 0}
          </strong>

        </div>


        <div className="stat-card">

          <span>
            System Status
          </span>

          <strong
            className={
              monitoring
                ? "text-success"
                : "text-warning"
            }
          >
            {monitoring
              ? "ONLINE"
              : "STOPPED"}
          </strong>

        </div>

      </div>

    </div>

  );
}

export default LiveMonitoring;