import React, { useEffect, useState } from "react";

const API_BASE = "http://localhost:5000";

function IoTDevices() {

    const [iot, setIot] = useState({
        connected: false,
        ip: "Unknown",
        alarm: "OFF",
        servo: 0,
        state: "NORMAL"
    });

    const [loading, setLoading] = useState(true);


    // ==================================================
    // LOAD IOT STATUS
    // ==================================================

    const loadStatus = async () => {

        try {

            const response = await fetch(
                `${API_BASE}/api/iot/status`
            );

            if (!response.ok) {

                throw new Error(
                    "IoT status request failed"
                );
            }

            const data = await response.json();

            setIot(data);

        } catch (error) {

            console.error(
                "IoT status error:",
                error
            );

            setIot({
                connected: false,
                ip: "Unknown",
                alarm: "OFF",
                servo: 0,
                state: "OFFLINE"
            });

        } finally {

            setLoading(false);
        }
    };


    // ==================================================
    // POLLING
    // ==================================================

    useEffect(() => {

        loadStatus();

        const interval = setInterval(
            loadStatus,
            1000
        );

        return () => {
            clearInterval(interval);
        };

    }, []);


    const connected =
        Boolean(iot?.connected);


    return (
        <div className="page">

            {/* =========================================
                HEADER
            ========================================= */}

            <div className="page-header">

                <div>

                    <h1>
                        IoT Devices
                    </h1>

                    <p>
                        AquaGuard hardware status
                    </p>

                </div>

            </div>


            {/* =========================================
                DEVICE GRID
            ========================================= */}

            <div className="device-grid">


                {/* =====================================
                    ESP8266
                ===================================== */}

                <div className="device-card">

                    <div className="device-card-header">

                        <h3>
                            ESP8266 NodeMCU
                        </h3>

                        <span
                            className={
                                connected
                                    ? "status-badge safe"
                                    : "status-badge danger"
                            }
                        >
                            {
                                connected
                                    ? "Online"
                                    : "Offline"
                            }
                        </span>

                    </div>

                    <p>
                        IP Address
                    </p>

                    <strong>
                        {iot?.ip || "Unknown"}
                    </strong>

                </div>


                {/* =====================================
                    BUZZER
                ===================================== */}

                <div className="device-card">

                    <div className="device-card-header">

                        <h3>
                            Emergency Buzzer
                        </h3>

                        <span
                            className={
                                iot?.alarm === "ON"
                                    ? "status-badge danger"
                                    : "status-badge safe"
                            }
                        >
                            {iot?.alarm || "OFF"}
                        </span>

                    </div>

                    <p>
                        Current hardware state
                    </p>

                    <strong>

                        {
                            iot?.alarm === "ON"
                                ? "Beeping"
                                : "Silent"
                        }

                    </strong>

                </div>


                {/* =====================================
                    SERVO
                ===================================== */}

                <div className="device-card">

                    <div className="device-card-header">

                        <h3>
                            Rescue Servo
                        </h3>

                        <span className="status-badge">

                            {iot?.servo ?? 0}°

                        </span>

                    </div>

                    <p>
                        Current position
                    </p>

                    <strong>

                        {
                            iot?.servo === 180
                                ? "Emergency Position"
                                : "Normal Position"
                        }

                    </strong>

                </div>


                {/* =====================================
                    SYSTEM STATE
                ===================================== */}

                <div className="device-card">

                    <div className="device-card-header">

                        <h3>
                            System State
                        </h3>

                        <span
                            className={
                                iot?.state === "EMERGENCY"
                                    ? "status-badge danger"
                                    : "status-badge safe"
                            }
                        >
                            {
                                iot?.state ||
                                "UNKNOWN"
                            }
                        </span>

                    </div>

                    <p>
                        Hardware controller state
                    </p>

                    <strong>

                        {
                            loading
                                ? "Checking..."
                                : iot?.state === "EMERGENCY"
                                    ? "Emergency Active"
                                    : "Normal"
                        }

                    </strong>

                </div>

            </div>

        </div>
    );
}

export default IoTDevices;