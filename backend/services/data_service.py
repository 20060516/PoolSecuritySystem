import os
import json
import threading
from datetime import datetime


class DataService:

    def __init__(self, base_dir):

        self.data_dir = os.path.join(
            base_dir,
            "data"
        )

        os.makedirs(
            self.data_dir,
            exist_ok=True
        )

        self.incidents_file = os.path.join(
            self.data_dir,
            "incidents.json"
        )

        self.statistics_file = os.path.join(
            self.data_dir,
            "statistics.json"
        )

        self.lock = threading.Lock()

        self._create_files()

    # =========================================================
    # DEFAULT STATISTICS
    # =========================================================

    def _default_statistics(self):

        return {

            "total_predictions":
                0,

            "total_drowning":
                0,

            "total_safe":
                0,

            "confidence_history":
                [],

            "prediction_history":
                []
        }

    # =========================================================
    # CREATE / REPAIR FILES
    # =========================================================

    def _create_files(self):

        # =====================================================
        # INCIDENT FILE
        # =====================================================

        if not os.path.exists(
            self.incidents_file
        ):

            self._write_json(
                self.incidents_file,
                []
            )

        else:

            try:

                with open(
                    self.incidents_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    content = file.read().strip()

                    if not content:

                        raise ValueError(
                            "Empty incidents.json"
                        )

                    data = json.loads(
                        content
                    )

                    if not isinstance(
                        data,
                        list
                    ):

                        raise ValueError(
                            "incidents.json must contain a list"
                        )

            except Exception as error:

                print(
                    "WARNING: incidents.json is invalid."
                )

                print(
                    error
                )

                self._write_json(
                    self.incidents_file,
                    []
                )

        # =====================================================
        # STATISTICS FILE
        # =====================================================

        if not os.path.exists(
            self.statistics_file
        ):

            self._write_json(
                self.statistics_file,
                self._default_statistics()
            )

        else:

            try:

                with open(
                    self.statistics_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    content = file.read().strip()

                    if not content:

                        raise ValueError(
                            "Empty statistics.json"
                        )

                    data = json.loads(
                        content
                    )

                    if not isinstance(
                        data,
                        dict
                    ):

                        raise ValueError(
                            "statistics.json must contain an object"
                        )

            except Exception as error:

                print(
                    "WARNING: statistics.json is invalid."
                )

                print(
                    error
                )

                print(
                    "Repairing statistics.json..."
                )

                self._write_json(
                    self.statistics_file,
                    self._default_statistics()
                )

                print(
                    "statistics.json repaired."
                )

    # =========================================================
    # READ JSON SAFELY
    # =========================================================

    def _read_json(
        self,
        path,
        default
    ):

        try:

            # -------------------------------------------------
            # File does not exist
            # -------------------------------------------------

            if not os.path.exists(path):

                self._write_json(
                    path,
                    default
                )

                return default

            # -------------------------------------------------
            # Read file
            # -------------------------------------------------

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:

                content = (
                    file.read().strip()
                )

            # -------------------------------------------------
            # Empty file
            # -------------------------------------------------

            if not content:

                print(
                    f"WARNING: Empty JSON file: {path}"
                )

                self._write_json(
                    path,
                    default
                )

                return default

            # -------------------------------------------------
            # Parse JSON
            # -------------------------------------------------

            return json.loads(
                content
            )

        except json.JSONDecodeError as error:

            print(
                f"WARNING: Invalid JSON: {path}"
            )

            print(
                "JSON error:",
                error
            )

            # -------------------------------------------------
            # Repair corrupted file
            # -------------------------------------------------

            self._write_json(
                path,
                default
            )

            print(
                f"Repaired JSON file: {path}"
            )

            return default

        except Exception as error:

            print(
                f"ERROR reading JSON file: {path}"
            )

            print(
                error
            )

            return default

    # =========================================================
    # WRITE JSON SAFELY
    # =========================================================

    def _write_json(
        self,
        path,
        data
    ):

        temp_path = (
            path +
            ".tmp"
        )

        # -----------------------------------------------------
        # Write temporary file
        # -----------------------------------------------------

        with open(
            temp_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

        # -----------------------------------------------------
        # Replace original
        # -----------------------------------------------------

        os.replace(
            temp_path,
            path
        )

    # =========================================================
    # RECORD CNN PREDICTION
    # =========================================================

    def record_prediction(
        self,
        label,
        confidence,
        inference_ms
    ):

        with self.lock:

            statistics = self._read_json(

                self.statistics_file,

                self._default_statistics()
            )

            # -------------------------------------------------
            # Make sure structure exists
            # -------------------------------------------------

            if not isinstance(
                statistics,
                dict
            ):

                statistics = (
                    self._default_statistics()
                )

            statistics.setdefault(
                "total_predictions",
                0
            )

            statistics.setdefault(
                "total_drowning",
                0
            )

            statistics.setdefault(
                "total_safe",
                0
            )

            statistics.setdefault(
                "confidence_history",
                []
            )

            statistics.setdefault(
                "prediction_history",
                []
            )

            # -------------------------------------------------
            # Total predictions
            # -------------------------------------------------

            statistics[
                "total_predictions"
            ] += 1

            # -------------------------------------------------
            # Class counter
            # -------------------------------------------------

            if label == "DROWNING":

                statistics[
                    "total_drowning"
                ] += 1

            elif label == "NON-DROWNING":

                statistics[
                    "total_safe"
                ] += 1

            # -------------------------------------------------
            # Timestamp
            # -------------------------------------------------

            timestamp = (
                datetime.now().isoformat()
            )

            # -------------------------------------------------
            # Confidence history
            # -------------------------------------------------

            statistics[
                "confidence_history"
            ].append({

                "timestamp":
                    timestamp,

                "confidence":
                    confidence,

                "label":
                    label,

                "inference_ms":
                    inference_ms
            })

            # -------------------------------------------------
            # Prediction history
            # -------------------------------------------------

            statistics[
                "prediction_history"
            ].append({

                "timestamp":
                    timestamp,

                "label":
                    label,

                "confidence":
                    confidence
            })

            # -------------------------------------------------
            # Keep latest 500 records
            # -------------------------------------------------

            statistics[
                "confidence_history"
            ] = (
                statistics[
                    "confidence_history"
                ][-500:]
            )

            statistics[
                "prediction_history"
            ] = (
                statistics[
                    "prediction_history"
                ][-500:]
            )

            # -------------------------------------------------
            # Save
            # -------------------------------------------------

            self._write_json(

                self.statistics_file,

                statistics
            )

    # =========================================================
    # GET STATISTICS
    # =========================================================

    def get_statistics(self):

        with self.lock:

            statistics = self._read_json(

                self.statistics_file,

                self._default_statistics()
            )

            if not isinstance(
                statistics,
                dict
            ):

                statistics = (
                    self._default_statistics()
                )

            return statistics

    # =========================================================
    # CREATE INCIDENT
    # =========================================================

    def create_incident(
        self,
        confidence,
        duration,
        alarm_status,
        iot_status,
        sms_status
    ):

        with self.lock:

            incidents = self._read_json(

                self.incidents_file,

                []
            )

            if not isinstance(
                incidents,
                list
            ):

                incidents = []

            # -------------------------------------------------
            # Generate next ID
            # -------------------------------------------------

            if incidents:

                try:

                    next_id = (
                        max(
                            int(
                                item.get(
                                    "id",
                                    0
                                )
                            )
                            for item in incidents
                        )
                        + 1
                    )

                except Exception:

                    next_id = (
                        len(incidents)
                        + 1
                    )

            else:

                next_id = 1

            # -------------------------------------------------
            # Create incident
            # -------------------------------------------------

            incident = {

                "id":
                    next_id,

                "timestamp":
                    datetime.now().isoformat(),

                "type":
                    "DROWNING",

                "confidence":
                    confidence,

                "duration":
                    duration,

                "alarm":
                    alarm_status,

                "iot":
                    iot_status,

                "sms":
                    sms_status,

                "status":
                    "CONFIRMED"
            }

            # -------------------------------------------------
            # Newest incident first
            # -------------------------------------------------

            incidents.insert(
                0,
                incident
            )

            # -------------------------------------------------
            # Save
            # -------------------------------------------------

            self._write_json(

                self.incidents_file,

                incidents
            )

            return incident

    # =========================================================
    # GET INCIDENTS
    # =========================================================

    def get_incidents(self):

        with self.lock:

            incidents = self._read_json(

                self.incidents_file,

                []
            )

            if not isinstance(
                incidents,
                list
            ):

                return []

            return incidents

    # =========================================================
    # CLEAR STATISTICS
    # =========================================================

    def clear_statistics(self):

        with self.lock:

            self._write_json(

                self.statistics_file,

                self._default_statistics()
            )

            print(
                "Statistics cleared."
            )