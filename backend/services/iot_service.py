import os
import requests


class IoTService:

    def __init__(self, esp8266_ip=None):

        self.esp8266_ip = (
            esp8266_ip
            or os.getenv(
                "ESP8266_IP",
                "192.168.43.38"
            )
        )

        self.timeout = float(
            os.getenv(
                "IOT_TIMEOUT",
                "2.0"
            )
        )

        self.connected = False
        self.alarm_state = "OFF"
        self.servo_angle = 0

    # ==================================================
    # SEND REQUEST
    # ==================================================

    def _request(self, endpoint):

        url = f"http://{self.esp8266_ip}{endpoint}"

        print(
            f"[IoT] Sending GET request: {url}"
        )

        try:

            response = requests.get(
                url,
                timeout=self.timeout
            )

            print(
                f"[IoT] ESP8266 response: "
                f"{response.status_code}"
            )

            if response.status_code != 200:

                self.connected = False

                print(
                    f"[IoT] HTTP error: "
                    f"{response.status_code}"
                )

                return None

            self.connected = True

            try:

                data = response.json()

            except ValueError:

                print(
                    "[IoT] ESP8266 returned "
                    "non-JSON response."
                )

                data = {}

            # ------------------------------------------
            # Update cached state
            # ------------------------------------------

            if "alarm" in data:

                self.alarm_state = str(
                    data["alarm"]
                ).upper()

            if "servo" in data:

                try:

                    self.servo_angle = int(
                        data["servo"]
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    pass

            print(
                "[IoT] Request successful."
            )

            return data

        except requests.exceptions.Timeout as error:

            self.connected = False

            print(
                f"[IoT] ESP8266 timeout: {error}"
            )

            return None

        except requests.exceptions.ConnectionError as error:

            self.connected = False

            print(
                f"[IoT] ESP8266 connection error: {error}"
            )

            return None

        except requests.RequestException as error:

            self.connected = False

            print(
                f"[IoT] ESP8266 request error: {error}"
            )

            return None

        except Exception as error:

            self.connected = False

            print(
                f"[IoT] Unexpected IoT error: {error}"
            )

            return None

    # ==================================================
    # CONNECT
    # ==================================================

    def connect(self):

        print()
        print(
            "Checking ESP8266 connection..."
        )

        print(
            "ESP8266 IP:",
            self.esp8266_ip
        )

        data = self._request(
            "/status"
        )

        if data is not None:

            self.connected = True

            print(
                "IoT status: CONNECTED"
            )

            print(
                "ESP8266 IP:",
                self.esp8266_ip
            )

            return True

        self.connected = False

        print(
            "IoT status: DISCONNECTED"
        )

        return False

    # ==================================================
    # SEND ALARM
    # ==================================================

    def send_alarm(self, state):

        if state:

            endpoint = "/emergency"

            print()
            print(
                "================================"
            )
            print(
                "Sending emergency command to ESP8266"
            )
            print(
                "================================"
            )

        else:

            endpoint = "/reset"

            print(
                "[IoT] Sending reset command "
                "to ESP8266"
            )

        data = self._request(
            endpoint
        )

        if data is None:

            print(
                "[IoT] Emergency command failed."
                if state
                else
                "[IoT] Reset command failed."
            )

            return False

        # ------------------------------------------
        # Update local state
        # ------------------------------------------

        if state:

            self.alarm_state = "ON"
            self.servo_angle = 180

            print(
                "ESP8266 response: 200"
            )

            print(
                "IoT status: CONNECTED"
            )

            print(
                "Emergency command successful"
            )

            print(
                "Buzzer: ON"
            )

            print(
                "Servo: 180"
            )

        else:

            self.alarm_state = "OFF"
            self.servo_angle = 0

            print(
                "ESP8266 reset successful"
            )

            print(
                "Buzzer: OFF"
            )

            print(
                "Servo: 0"
            )

        return True

    # ==================================================
    # GET STATUS
    # ==================================================

    def get_status(self):

        self._request(
            "/status"
        )

        return self.get_cached_status()

    # ==================================================
    # CACHED STATUS
    # ==================================================

    def get_cached_status(self):

        return {

            "connected":
                self.connected,

            "ip":
                self.esp8266_ip,

            "alarm":
                self.alarm_state,

            "servo":
                self.servo_angle,

            "state":
                (
                    "EMERGENCY"
                    if self.alarm_state == "ON"
                    else "NORMAL"
                )
        }

    # ==================================================
    # CLOSE
    # ==================================================

    def close(self):

        self.connected = False