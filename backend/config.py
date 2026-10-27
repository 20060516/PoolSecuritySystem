import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.getenv(
    "MODEL_PATH",
    os.path.join(BASE_DIR, "model", "trained_model.h5")
)

VIDEO_SOURCE = os.getenv(
    "VIDEO_SOURCE",
    os.path.join(BASE_DIR, "media", "video.mp4")
)

SERIAL_PORT = os.getenv("SERIAL_PORT", "COM3")

SERIAL_BAUDRATE = int(
    os.getenv("SERIAL_BAUDRATE", "9600")
)

EMERGENCY_FRAMES = int(
    os.getenv("EMERGENCY_FRAMES", "30")
)

DROWNING_CLASS_INDEX = int(
    os.getenv("DROWNING_CLASS_INDEX", "0")
)

HOST = os.getenv("HOST", "0.0.0.0")

PORT = int(
    os.getenv("PORT", "5000")
)