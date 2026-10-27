import cv2
import time
import threading


class CameraService:

    def __init__(
        self,
        ml_service,
        video_source,
        data_service,
        iot_service=None,
        emergency_frames=1
    ):

        # ==================================================
        # SERVICES
        # ==================================================

        self.ml_service = ml_service
        self.video_source = video_source
        self.data_service = data_service
        self.iot_service = iot_service

        # ==================================================
        # SETTINGS
        # ==================================================

        # 1 = trigger immediately when DROWNING is detected
        self.emergency_frames = emergency_frames

        self.iot_retry_interval = 2.0

        self.last_iot_command_time = 0.0

        # ==================================================
        # CAMERA
        # ==================================================

        self.camera = None
        self.running = False

        # ==================================================
        # THREADS
        # ==================================================

        self.capture_thread = None
        self.inference_thread = None

        # ==================================================
        # FRAMES
        # ==================================================

        self.latest_frame = None
        self.inference_frame = None

        # ==================================================
        # LOCK
        # ==================================================

        self.lock = threading.Lock()

        # ==================================================
        # VIDEO
        # ==================================================

        self.video_fps = 25.0
        self.last_frame_time = time.time()

        # ==================================================
        # EMERGENCY
        # ==================================================

        self.consecutive_drowning = 0

        self.incident_active = False

        self.incident_start_time = None

        # Track previous CNN state
        self.previous_label = "WAITING"

        # ==================================================
        # STATISTICS
        # ==================================================

        self.total_predictions = 0
        self.total_drowning = 0
        self.total_safe = 0

        # ==================================================
        # LATEST PREDICTION
        # ==================================================

        self.latest_prediction = {

            "label": "WAITING",

            "confidence": 0,

            "confidence_percent": 0,

            "inference_ms": 0,

            "fps": 0,

            "consecutive_drowning": 0,

            "alarm": "OFF",

            "incident_active": False,

            "total_predictions": 0,

            "total_drowning": 0,

            "total_safe": 0,

            "running": False,

            "iot": "DISCONNECTED",

            "iot_alarm": "OFF",

            "servo_angle": 0,

            "sms": "READY"
        }

    # ======================================================
    # START
    # ======================================================

    def start(self):

        if self.running:

            return False

        print()
        print(
            "========================================"
        )
        print(
            "Starting AquaGuard monitoring..."
        )
        print(
            "Video:",
            self.video_source
        )
        print(
            "========================================"
        )

        # --------------------------------------------------
        # Open video
        # --------------------------------------------------

        self.camera = cv2.VideoCapture(
            self.video_source
        )

        if not self.camera.isOpened():

            print(
                "ERROR: Unable to open video."
            )

            self.camera = None

            return False

        # --------------------------------------------------
        # Get original FPS
        # --------------------------------------------------

        detected_fps = self.camera.get(
            cv2.CAP_PROP_FPS
        )

        if (
            detected_fps is None
            or detected_fps <= 0
            or detected_fps > 120
        ):

            self.video_fps = 25.0

        else:

            self.video_fps = float(
                detected_fps
            )

        print(
            f"Video FPS: {self.video_fps:.2f}"
        )

        print(
            f"Video playback FPS: "
            f"{self.video_fps:.2f}"
        )

        # --------------------------------------------------
        # Video duration
        # --------------------------------------------------

        frame_count = self.camera.get(
            cv2.CAP_PROP_FRAME_COUNT
        )

        if frame_count > 0:

            duration = (
                frame_count
                / self.video_fps
            )

            print(
                f"Video duration: "
                f"{duration:.2f} seconds"
            )

        else:

            print(
                "Video duration: unavailable"
            )

        # --------------------------------------------------
        # Reset state
        # --------------------------------------------------

        self.consecutive_drowning = 0

        self.incident_active = False

        self.incident_start_time = None

        self.previous_label = "WAITING"

        self.latest_prediction["label"] = (
            "WAITING"
        )

        self.latest_prediction["alarm"] = (
            "OFF"
        )

        # --------------------------------------------------
        # Reset hardware
        # --------------------------------------------------

        if self.iot_service is not None:

            success = (
                self.iot_service.send_alarm(
                    False
                )
            )

            self.last_iot_command_time = (
                time.time()
            )

            if success:

                print(
                    "IoT hardware reset successfully."
                )

            else:

                print(
                    "WARNING: ESP8266 reset failed."
                )

        # --------------------------------------------------
        # Start
        # --------------------------------------------------

        self.running = True

        self.latest_prediction[
            "running"
        ] = True

        # --------------------------------------------------
        # Capture thread
        # --------------------------------------------------

        self.capture_thread = threading.Thread(
            target=self._capture_video,
            daemon=True
        )

        self.capture_thread.start()

        print(
            "Video capture thread started."
        )

        # --------------------------------------------------
        # Inference thread
        # --------------------------------------------------

        self.inference_thread = threading.Thread(
            target=self._run_inference,
            daemon=True
        )

        self.inference_thread.start()

        print(
            "CNN inference thread started."
        )

        print(
            "AquaGuard monitoring started."
        )

        return True

    # ======================================================
    # CAPTURE VIDEO
    # ======================================================

    def _capture_video(self):

        frame_interval = 1.0 / self.video_fps

        next_frame_time = time.perf_counter()

        while self.running:

            if self.camera is None:

                break

            current_time = time.perf_counter()

            if current_time < next_frame_time:

                time.sleep(
                    next_frame_time
                    - current_time
                )

                continue

            # ------------------------------------------------
            # Read one frame
            # ------------------------------------------------

            success, frame = (
                self.camera.read()
            )

            # ------------------------------------------------
            # Restart video
            # ------------------------------------------------

            if not success:

                print(
                    "Video reached end. Restarting..."
                )

                self.camera.set(
                    cv2.CAP_PROP_POS_FRAMES,
                    0
                )

                next_frame_time = (
                    time.perf_counter()
                    + frame_interval
                )

                continue

            # ------------------------------------------------
            # Store frame
            # ------------------------------------------------

            with self.lock:

                self.latest_frame = frame

                self.inference_frame = (
                    frame.copy()
                )

            # ------------------------------------------------
            # Schedule next frame
            # ------------------------------------------------

            next_frame_time += frame_interval

            # Prevent timing drift
            if (
                time.perf_counter()
                - next_frame_time
                > frame_interval
            ):

                next_frame_time = (
                    time.perf_counter()
                    + frame_interval
                )

        print(
            "Video capture thread stopped."
        )

    # ======================================================
    # CNN INFERENCE
    # ======================================================

    def _run_inference(self):

        print(
            "CNN inference thread running."
        )

        while self.running:

            # ------------------------------------------------
            # Get latest frame
            # ------------------------------------------------

            with self.lock:

                if self.inference_frame is None:

                    frame = None

                else:

                    frame = (
                        self.inference_frame.copy()
                    )

                    self.inference_frame = None

            if frame is None:

                time.sleep(0.01)

                continue

            # ------------------------------------------------
            # CNN
            # ------------------------------------------------

            try:

                result = (
                    self.ml_service.predict_frame(
                        frame
                    )
                )

            except Exception as error:

                print(
                    "Prediction error:",
                    error
                )

                time.sleep(0.05)

                continue

            label = str(
                result.get(
                    "label",
                    "WAITING"
                )
            ).strip().upper()

            confidence = result.get(
                "confidence",
                0
            )

            confidence_percent = result.get(
                "confidence_percent",
                0
            )

            inference_ms = result.get(
                "inference_ms",
                0
            )

            # ------------------------------------------------
            # Statistics
            # ------------------------------------------------

            self.total_predictions += 1

            if label == "DROWNING":

                self.total_drowning += 1

                self.consecutive_drowning += 1

            elif label == "NON-DROWNING":

                self.total_safe += 1

                self.consecutive_drowning = 0

            else:

                # WAITING should not be treated as safe
                self.consecutive_drowning = 0

            # ------------------------------------------------
            # STATE CHANGE
            # ------------------------------------------------

            state_changed = (
                label != self.previous_label
            )

            # ------------------------------------------------
            # DROWNING
            # ------------------------------------------------

            if label == "DROWNING":

                if not self.incident_active:

                    self.incident_active = True

                    self.incident_start_time = (
                        time.time()
                    )

                    print()
                    print(
                        "================================"
                    )
                    print(
                        "DROWNING detected"
                    )
                    print(
                        "================================"
                    )

                    # ----------------------------------------
                    # SEND EMERGENCY ONLY ONCE
                    # ----------------------------------------

                    if self.iot_service is not None:

                        print(
                            "Sending emergency command "
                            "to ESP8266"
                        )

                        success = (
                            self.iot_service.send_alarm(
                                True
                            )
                        )

                        self.last_iot_command_time = (
                            time.time()
                        )

                        if success:

                            print(
                                "ESP8266 response: 200"
                            )

                            print(
                                "IoT status: CONNECTED"
                            )

                            print(
                                "Emergency command successful"
                            )

                        else:

                            print(
                                "ESP8266 emergency "
                                "command failed."
                            )

                alarm = "ON"

            # ------------------------------------------------
            # NON-DROWNING
            # ------------------------------------------------

            elif label == "NON-DROWNING":

                alarm = "OFF"

                # --------------------------------------------
                # DROWNING → NON-DROWNING
                # --------------------------------------------

                if self.incident_active:

                    print()
                    print(
                        "================================"
                    )
                    print(
                        "DROWNING cleared"
                    )
                    print(
                        "Sending reset command to ESP8266"
                    )
                    print(
                        "================================"
                    )

                    if self.iot_service is not None:

                        success = (
                            self.iot_service.send_alarm(
                                False
                            )
                        )

                        self.last_iot_command_time = (
                            time.time()
                        )

                        if success:

                            print(
                                "ESP8266 response: 200"
                            )

                            print(
                                "IoT status: CONNECTED"
                            )

                            print(
                                "Reset command successful"
                            )

                        else:

                            print(
                                "ESP8266 reset "
                                "command failed."
                            )

                    # ----------------------------------------
                    # Save incident
                    # ----------------------------------------

                    end_time = time.time()

                    duration = 0

                    if self.incident_start_time:

                        duration = (
                            end_time
                            - self.incident_start_time
                        )

                    try:

                        self.data_service.record_incident(
                            confidence=(
                                self.latest_prediction.get(
                                    "confidence_percent",
                                    0
                                )
                            ),
                            duration=duration,
                            alarm="ON",
                            iot=(
                                "CONNECTED"
                                if (
                                    self.iot_service
                                    and
                                    self.iot_service.connected
                                )
                                else
                                "DISCONNECTED"
                            )
                        )

                    except Exception as error:

                        print(
                            "Incident save error:",
                            error
                        )

                    # ----------------------------------------
                    # Clear emergency
                    # ----------------------------------------

                    self.incident_active = False

                    self.incident_start_time = None

                    self.consecutive_drowning = 0

            # ------------------------------------------------
            # WAITING
            # ------------------------------------------------

            else:

                alarm = (
                    "ON"
                    if self.incident_active
                    else "OFF"
                )

            # ------------------------------------------------
            # Save current prediction
            # ------------------------------------------------

            self.previous_label = label

            # ------------------------------------------------
            # IoT STATUS
            # ------------------------------------------------

            if self.iot_service is not None:

                iot_status = (
                    "CONNECTED"
                    if self.iot_service.connected
                    else "DISCONNECTED"
                )

                iot_alarm = (
                    self.iot_service.alarm_state
                )

                servo_angle = (
                    self.iot_service.servo_angle
                )

            else:

                iot_status = "DISCONNECTED"

                iot_alarm = "OFF"

                servo_angle = 0

            # ------------------------------------------------
            # Detection FPS
            # ------------------------------------------------

            current_time = time.time()

            elapsed = (
                current_time
                - self.last_frame_time
            )

            if elapsed > 0:

                current_fps = (
                    1.0 / elapsed
                )

            else:

                current_fps = 0

            self.last_frame_time = current_time

            # ------------------------------------------------
            # Data service
            # ------------------------------------------------

            try:

                self.data_service.record_prediction(
                    label=label,
                    confidence=confidence_percent
                )

            except TypeError:

                try:

                    self.data_service.record_prediction(
                        label,
                        confidence_percent
                    )

                except Exception:
                    pass

            except Exception:
                pass

            # ------------------------------------------------
            # Update status
            # ------------------------------------------------

            with self.lock:

                self.latest_prediction = {

                    "label":
                        label,

                    "confidence":
                        confidence,

                    "confidence_percent":
                        confidence_percent,

                    "inference_ms":
                        inference_ms,

                    "fps":
                        round(
                            current_fps,
                            2
                        ),

                    "consecutive_drowning":
                        self.consecutive_drowning,

                    "alarm":
                        alarm,

                    "incident_active":
                        self.incident_active,

                    "total_predictions":
                        self.total_predictions,

                    "total_drowning":
                        self.total_drowning,

                    "total_safe":
                        self.total_safe,

                    "running":
                        self.running,

                    "iot":
                        iot_status,

                    "iot_alarm":
                        iot_alarm,

                    "servo_angle":
                        servo_angle,

                    "sms":
                        "READY"
                }

        print(
            "CNN inference thread stopped."
        )

    # ======================================================
    # GET CURRENT FRAME
    # ======================================================

    def get_frame(self):

        with self.lock:

            if self.latest_frame is None:

                return None

            frame = (
                self.latest_frame.copy()
            )

            status = (
                self.latest_prediction.copy()
            )

        label = status.get(
            "label",
            "WAITING"
        )

        confidence = status.get(
            "confidence_percent",
            0
        )

        fps = status.get(
            "fps",
            0
        )

        inference_ms = status.get(
            "inference_ms",
            0
        )

        incident_active = status.get(
            "incident_active",
            False
        )

        # --------------------------------------------------
        # Label
        # --------------------------------------------------

        cv2.putText(
            frame,
            f"Status: {label}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (
                (0, 0, 255)
                if label == "DROWNING"
                else
                (0, 255, 0)
            ),
            2
        )

        # --------------------------------------------------
        # Confidence
        # --------------------------------------------------

        cv2.putText(
            frame,
            f"Confidence: {confidence:.2f}%",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # --------------------------------------------------
        # Detection FPS
        # --------------------------------------------------

        cv2.putText(
            frame,
            f"ML FPS: {fps:.2f}",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        # --------------------------------------------------
        # Inference
        # --------------------------------------------------

        cv2.putText(
            frame,
            f"Inference: {inference_ms:.2f} ms",
            (20, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        # --------------------------------------------------
        # Emergency
        # --------------------------------------------------

        if incident_active:

            cv2.rectangle(
                frame,
                (5, 5),
                (
                    frame.shape[1] - 5,
                    frame.shape[0] - 5
                ),
                (0, 0, 255),
                4
            )

            cv2.putText(
                frame,
                "!!! EMERGENCY !!!",
                (20, 170),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                3
            )

        # --------------------------------------------------
        # JPEG
        # --------------------------------------------------

        success, buffer = cv2.imencode(
            ".jpg",
            frame
        )

        if not success:

            return None

        return buffer.tobytes()

    # ======================================================
    # VIDEO STREAM
    # ======================================================

    def generate_video(self):

        frame_interval = (
            1.0 / self.video_fps
        )

        next_frame_time = (
            time.perf_counter()
        )

        while self.running:

            current_time = (
                time.perf_counter()
            )

            if current_time < next_frame_time:

                time.sleep(
                    next_frame_time
                    - current_time
                )

                continue

            frame = self.get_frame()

            if frame is not None:

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + frame
                    + b"\r\n"
                )

            next_frame_time += frame_interval

            if (
                time.perf_counter()
                - next_frame_time
                > frame_interval
            ):

                next_frame_time = (
                    time.perf_counter()
                    + frame_interval
                )

    # ======================================================
    # STATUS
    # ======================================================

    def get_status(self):

        with self.lock:

            return (
                self.latest_prediction.copy()
            )

    # ======================================================
    # MANUAL RESET
    # ======================================================

    def reset(self):

        if self.incident_active:

            end_time = time.time()

            duration = 0

            if self.incident_start_time:

                duration = (
                    end_time
                    - self.incident_start_time
                )

            try:

                self.data_service.record_incident(
                    confidence=(
                        self.latest_prediction.get(
                            "confidence_percent",
                            0
                        )
                    ),
                    duration=duration,
                    alarm="ON",
                    iot=(
                        "CONNECTED"
                        if (
                            self.iot_service
                            and self.iot_service.connected
                        )
                        else
                        "DISCONNECTED"
                    )
                )

            except Exception as error:

                print(
                    "Incident save error:",
                    error
                )

        # --------------------------------------------------
        # Reset ESP8266
        # --------------------------------------------------

        if self.iot_service is not None:

            success = (
                self.iot_service.send_alarm(
                    False
                )
            )

            self.last_iot_command_time = (
                time.time()
            )

            if success:

                print(
                    "ESP8266 reset command sent."
                )

            else:

                print(
                    "WARNING: ESP8266 reset failed."
                )

        # --------------------------------------------------
        # Reset state
        # --------------------------------------------------

        self.consecutive_drowning = 0

        self.incident_active = False

        self.incident_start_time = None

        self.previous_label = "NON-DROWNING"

        with self.lock:

            self.latest_prediction[
                "consecutive_drowning"
            ] = 0

            self.latest_prediction[
                "alarm"
            ] = "OFF"

            self.latest_prediction[
                "incident_active"
            ] = False

            if self.iot_service is not None:

                self.latest_prediction[
                    "iot"
                ] = (
                    "CONNECTED"
                    if self.iot_service.connected
                    else "DISCONNECTED"
                )

                self.latest_prediction[
                    "iot_alarm"
                ] = (
                    self.iot_service.alarm_state
                )

                self.latest_prediction[
                    "servo_angle"
                ] = (
                    self.iot_service.servo_angle
                )

        print(
            "AquaGuard emergency reset."
        )

        return True

    # ======================================================
    # STOP
    # ======================================================

    def stop(self):

        if not self.running:

            return True

        print(
            "Stopping AquaGuard monitoring..."
        )

        self.running = False

        self.latest_prediction[
            "running"
        ] = False

        if (
            self.capture_thread
            and self.capture_thread.is_alive()
        ):

            self.capture_thread.join(
                timeout=2
            )

        if (
            self.inference_thread
            and self.inference_thread.is_alive()
        ):

            self.inference_thread.join(
                timeout=2
            )

        # --------------------------------------------------
        # Reset hardware
        # --------------------------------------------------

        if self.iot_service is not None:

            self.iot_service.send_alarm(
                False
            )

            self.latest_prediction[
                "iot"
            ] = (
                "CONNECTED"
                if self.iot_service.connected
                else "DISCONNECTED"
            )

            self.latest_prediction[
                "iot_alarm"
            ] = self.iot_service.alarm_state

            self.latest_prediction[
                "servo_angle"
            ] = self.iot_service.servo_angle

        # --------------------------------------------------
        # Release video
        # --------------------------------------------------

        if self.camera is not None:

            self.camera.release()

            self.camera = None

        print(
            "AquaGuard monitoring stopped."
        )

        return True