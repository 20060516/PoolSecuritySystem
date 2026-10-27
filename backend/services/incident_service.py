import os
import json
from datetime import datetime


class IncidentService:

    def __init__(self, data_file):

        self.data_file = data_file

        directory = os.path.dirname(
            data_file
        )

        os.makedirs(
            directory,
            exist_ok=True
        )

        if not os.path.exists(data_file):

            with open(
                data_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    [],
                    file
                )

    def get_incidents(self):

        try:

            with open(
                self.data_file,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except Exception:

            return []

    def add_incident(
        self,
        confidence,
        duration=0
    ):

        incidents = self.get_incidents()

        incident = {

            "id": len(incidents) + 1,

            "timestamp":
                datetime.now().isoformat(
                    timespec="seconds"
                ),

            "prediction":
                "DROWNING",

            "confidence":
                round(
                    confidence * 100,
                    2
                ),

            "duration_seconds":
                round(
                    duration,
                    2
                ),

            "alarm":
                True,

            "sms":
                False

        }

        incidents.append(
            incident
        )

        with open(
            self.data_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                incidents,
                file,
                indent=4
            )

        return incident