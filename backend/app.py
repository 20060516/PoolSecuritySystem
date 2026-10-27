import os

from flask import (
    Flask,
    jsonify,
    Response,
    send_from_directory
)

from flask_cors import CORS

from services.ml_service import MLService
from services.camera_service import CameraService
from services.data_service import DataService
from services.iot_service import IoTService


# ======================================================
# FLASK
# ======================================================

app = Flask(__name__)

CORS(app)


# ======================================================
# BASE DIRECTORY
# ======================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ======================================================
# PATHS
# ======================================================

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model",
    "trained_model.h5"
)

VIDEO_SOURCE = os.path.join(
    BASE_DIR,
    "media",
    "video.mp4"
)


# ======================================================
# SERVICES
# ======================================================

print()
print("========================================")
print("AquaGuard Pool Safety System")
print("========================================")


# ------------------------------------------------------
# Data Service
# ------------------------------------------------------

data_service = DataService(
    BASE_DIR
)


# ------------------------------------------------------
# ML Service
# ------------------------------------------------------

print("----------------------------------------")
print("Loading CNN model...")
print(
    "Model:",
    MODEL_PATH
)

ml_service = MLService(
    MODEL_PATH
)

print("----------------------------------------")


# ------------------------------------------------------
# IoT Service
# ------------------------------------------------------

iot_service = IoTService()

if iot_service.connect():

    print(
        "IoT: ESP8266 connected at",
        iot_service.esp8266_ip
    )

else:

    print(
        "WARNING: ESP8266 is not connected."
    )

    print(
        "Monitoring can still run without IoT."
    )


# ------------------------------------------------------
# Camera Service
# ------------------------------------------------------

camera_service = CameraService(

    ml_service=ml_service,

    video_source=VIDEO_SOURCE,

    data_service=data_service,

    iot_service=iot_service,

    emergency_frames=1
)


# ======================================================
# HOME
# ======================================================

@app.route("/")
def home():

    return jsonify({

        "system":
            "AquaGuard Pool Safety System",

        "status":
            "online",

        "iot":
            iot_service.get_cached_status()

    })


# ======================================================
# HEALTH
# ======================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "status": "healthy",

        "model": "loaded",

        "iot":
            iot_service.get_cached_status()

    })


# ======================================================
# START MONITORING
# ======================================================

@app.route(
    "/api/monitoring/start",
    methods=["POST"]
)
def start_monitoring():

    success = camera_service.start()

    if success:

        return jsonify({

            "success": True,

            "message":
                "AquaGuard monitoring started."

        })

    return jsonify({

        "success": False,

        "message":
            "Unable to start monitoring."

    }), 500


# ======================================================
# STOP MONITORING
# ======================================================

@app.route(
    "/api/monitoring/stop",
    methods=["POST"]
)
def stop_monitoring():

    success = camera_service.stop()

    return jsonify({

        "success": success,

        "message":
            "AquaGuard monitoring stopped."

    })


# ======================================================
# VIDEO STREAM
# ======================================================

@app.route(
    "/video"
)
def video():

    return Response(

        camera_service.generate_video(),

        mimetype=(
            "multipart/x-mixed-replace; "
            "boundary=frame"
        )

    )


# ======================================================
# MEDIA
# ======================================================

@app.route(
    "/media/<path:filename>"
)
def media(filename):

    media_directory = os.path.join(
        BASE_DIR,
        "media"
    )

    return send_from_directory(
        media_directory,
        filename
    )


# ======================================================
# CAMERA STATUS
# ======================================================

@app.route(
    "/api/status",
    methods=["GET"]
)
def get_status():

    status = camera_service.get_status()

    iot = iot_service.get_cached_status()

    status["iot"] = (
        "CONNECTED"
        if iot["connected"]
        else "DISCONNECTED"
    )

    status["iot_alarm"] = (
        iot["alarm"]
    )

    status["servo_angle"] = (
        iot["servo"]
    )

    return jsonify(status)


# ======================================================
# PREDICTION
# ======================================================

@app.route(
    "/api/prediction",
    methods=["GET"]
)
def prediction():

    return jsonify(
        camera_service.get_status()
    )


# ======================================================
# IOT STATUS
# ======================================================

@app.route(
    "/api/iot/status",
    methods=["GET"]
)
def iot_status():

    return jsonify(
        iot_service.get_status()
    )


# ======================================================
# STATISTICS
# ======================================================

@app.route(
    "/api/statistics",
    methods=["GET"]
)
def statistics():

    stats = data_service.get_statistics()

    total = stats.get(
        "total_predictions",
        0
    )

    drowning = stats.get(
        "drowning_count",
        0
    )

    safe = stats.get(
        "safe_count",
        0
    )

    if total > 0:

        drowning_percentage = (
            drowning / total
        ) * 100

        safe_percentage = (
            safe / total
        ) * 100

    else:

        drowning_percentage = 0

        safe_percentage = 0

    stats["drowning_percentage"] = round(
        drowning_percentage,
        2
    )

    stats["safe_percentage"] = round(
        safe_percentage,
        2
    )

    return jsonify(stats)


# ======================================================
# INCIDENTS
# ======================================================

@app.route(
    "/api/incidents",
    methods=["GET"]
)
def incidents():

    return jsonify(
        data_service.get_incidents()
    )


# ======================================================
# RESET EMERGENCY
# ======================================================

@app.route(
    "/api/emergency/reset",
    methods=["POST"]
)
def reset_emergency():

    success = camera_service.reset()

    return jsonify({

        "success": success,

        "message":
            "Emergency reset successfully.",

        "iot":
            iot_service.get_cached_status()

    })


# ======================================================
# SETTINGS
# ======================================================

@app.route(
    "/api/settings",
    methods=["GET"]
)
def settings():

    return jsonify({

        "video_source":
            VIDEO_SOURCE,

        "emergency_frames":
            30,

        "monitoring":
            camera_service.running,

        "model":
            MODEL_PATH,

        "image_size":
            "224x224",

        "iot":
            "ESP8266",

        "iot_ip":
            iot_service.esp8266_ip,

        "iot_status":
            iot_service.get_cached_status(),

        "notification":
            "SMS Ready"

    })


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":

    print()
    print("========================================")
    print("Starting Flask server")
    print("========================================")

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=False,

        threaded=True

    )