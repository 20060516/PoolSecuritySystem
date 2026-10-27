import { useEffect, useState } from "react";

const API = "http://localhost:5000";

function EmergencyCenter() {

  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadStatus = async () => {

    try {

      const response = await fetch(
        `${API}/api/status`,
        {
          cache: "no-store"
        }
      );

      if (!response.ok) {
        throw new Error(
          "Unable to get system status."
        );
      }

      const data = await response.json();

      setStatus(data);
      setError("");

    } catch (error) {

      console.error(
        "Emergency Center error:",
        error
      );

      setError(
        "Backend is not connected."
      );
    }
  };


  useEffect(() => {

    loadStatus();

    const interval =
      setInterval(
        loadStatus,
        1000
      );

    return () =>
      clearInterval(interval);

  }, []);


  const resetEmergency = async () => {

    if (loading) {
      return;
    }

    try {

      setLoading(true);
      setError("");

      const response =
        await fetch(
          `${API}/api/emergency/reset`,
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

      await loadStatus();

    } catch (error) {

      console.error(
        "Reset emergency error:",
        error
      );

      setError(
        error.message ||
        "Unable to reset emergency."
      );

    } finally {

      setLoading(false);
    }
  };


  const active =
    Boolean(status?.incident_active);

  const alarmOn =
    status?.alarm === "ON";

  const iotConnected =
    status?.iot === "CONNECTED";

  const prediction =
    status?.label ||
    "WAITING";


  return (

    <div className="page">

      {/* HEADER */}
      <div className="page-header">

        <div>

          <h1>
            Emergency Center
          </h1>

          <p>
            Real-time emergency response status
          </p>

        </div>

      </div>


      {/* ERROR */}
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


      {/* EMERGENCY STATUS */}
      <div
        className={
          active
            ? "card emergency-alert"
            : "card"
        }
      >

        <h2>

          {active
            ? "DROWNING DETECTED"
            : "SYSTEM NORMAL"}

        </h2>

        <p>

          {active
            ? "The CNN has detected a confirmed emergency condition."
            : "No active drowning emergency detected."}

        </p>

      </div>


      {/* STATUS CARDS */}
      <div className="stats-grid">

        {/* PREDICTION */}
        <div className="stat-card">

          <span>
            Prediction
          </span>

          <strong
            className={
              prediction === "DROWNING"
                ? "text-danger"
                : "text-success"
            }
          >

            {prediction}

          </strong>

        </div>


        {/* CONFIDENCE */}
        <div className="stat-card">

          <span>
            Confidence
          </span>

          <strong>
            {status?.confidence_percent ?? 0}%
          </strong>

        </div>


        {/* ALARM */}
        <div className="stat-card">

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


        {/* IOT */}
        <div className="stat-card">

          <span>
            IoT
          </span>

          <strong
            className={
              iotConnected
                ? "text-success"
                : "text-warning"
            }
          >

            {status?.iot ||
              "DISCONNECTED"}

          </strong>

        </div>

      </div>


      {/* EMERGENCY RESPONSE */}
      <div className="card">

        <div className="card-header">

          <div>

            <h2>
              Emergency Response
            </h2>

            <p>
              IoT and AI emergency response information
            </p>

          </div>

        </div>


        <div className="prediction-details">

          {/* CONSECUTIVE FRAMES */}
          <div className="detail-row">

            <span>
              Consecutive Drowning Frames
            </span>

            <strong
              className={
                (status?.consecutive_drowning ?? 0) > 0
                  ? "text-danger"
                  : "text-success"
              }
            >

              {status?.consecutive_drowning ?? 0}

            </strong>

          </div>


          {/* REQUIRED FRAMES */}
          <div className="detail-row">

            <span>
              Required Emergency Frames
            </span>

            <strong>
              30
            </strong>

          </div>


          {/* SMS */}
          <div className="detail-row">

            <span>
              SMS Status
            </span>

            <strong>
              {status?.sms || "READY"}
            </strong>

          </div>


          {/* ALARM */}
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

              {alarmOn
                ? "ON"
                : "OFF"}

            </strong>

          </div>


          {/* SERVO */}
          <div className="detail-row">

            <span>
              Rescue Servo
            </span>

            <strong>
              {status?.servo_angle ?? 0}°
            </strong>

          </div>


          {/* IOT CONNECTION */}
          <div className="detail-row">

            <span>
              ESP8266
            </span>

            <strong
              className={
                iotConnected
                  ? "text-success"
                  : "text-warning"
              }
            >

              {status?.iot ||
                "DISCONNECTED"}

            </strong>

          </div>


          {/* EMERGENCY */}
          <div className="detail-row">

            <span>
              Emergency
            </span>

            <strong
              className={
                active
                  ? "text-danger"
                  : "text-success"
              }
            >

              {active
                ? "ACTIVE"
                : "NORMAL"}

            </strong>

          </div>

        </div>


        {/* RESET BUTTON */}
        {active && (

          <button
            className="btn btn-danger"
            onClick={resetEmergency}
            disabled={loading}
          >

            {loading
              ? "Resetting..."
              : "Reset Emergency"}

          </button>

        )}

      </div>

    </div>
  );
}

export default EmergencyCenter;