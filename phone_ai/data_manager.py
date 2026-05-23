import json
import os
from datetime import datetime

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
_MESSAGES_FILE = os.path.join(_DATA_DIR, "messages.json")
_APPOINTMENTS_FILE = os.path.join(_DATA_DIR, "appointments.json")
_SCREEN_INQUIRIES_FILE = os.path.join(_DATA_DIR, "screen_inquiries.json")


class DataManager:
    def __init__(self):
        os.makedirs(_DATA_DIR, exist_ok=True)
        for path in (_MESSAGES_FILE, _APPOINTMENTS_FILE, _SCREEN_INQUIRIES_FILE):
            if not os.path.exists(path):
                with open(path, "w") as f:
                    json.dump([], f)

    def _load(self, path: str) -> list:
        with open(path) as f:
            return json.load(f)

    def _append(self, path: str, record: dict) -> dict:
        data = self._load(path)
        record["id"] = len(data) + 1
        record["received_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        data.append(record)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return record

    def log_message(self, record: dict) -> dict:
        record["status"] = "unread"
        return self._append(_MESSAGES_FILE, record)

    def log_appointment(self, record: dict) -> dict:
        return self._append(_APPOINTMENTS_FILE, record)

    def get_messages(self) -> list:
        return self._load(_MESSAGES_FILE)

    def get_appointments(self) -> list:
        return self._load(_APPOINTMENTS_FILE)

    def log_screen_inquiry(self, record: dict) -> dict:
        return self._append(_SCREEN_INQUIRIES_FILE, record)

    def get_screen_inquiries(self) -> list:
        return self._load(_SCREEN_INQUIRIES_FILE)
