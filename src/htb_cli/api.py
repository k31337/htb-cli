import base64
import json
import os

import httpx

BASE_URL = "https://labs.hackthebox.com/api/v4"


class HTBAPIError(Exception):
    pass


class HTBClient:
    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.environ.get("HTB_TOKEN")
        if not self.token:
            raise HTBAPIError(
                "HTB token not found. Set the HTB_TOKEN environment variable."
            )

    def _own_user_id(self) -> str:
        try:
            payload_segment = self.token.split(".")[1]
            padding = "=" * (-len(payload_segment) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_segment + padding))
            return str(payload["sub"])
        except (IndexError, ValueError, KeyError):
            raise HTBAPIError("Could not read user ID from the token.")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

    def get(self, path: str, params: dict | None = None) -> dict:
        url = f"{BASE_URL}{path}"
        response = httpx.get(url, headers=self._headers(), params=params, timeout=15)
        if response.status_code == 401:
            raise HTBAPIError("Invalid or expired token.")
        response.raise_for_status()
        return response.json()

    def active_machines(self) -> list[dict]:
        data = self.get("/machine/paginated")
        return data.get("data", data) if isinstance(data, dict) else data

    def machine_profile(self, id_or_name: str) -> dict:
        data = self.get(f"/machine/profile/{id_or_name}")
        return data.get("info", data) if isinstance(data, dict) else data

    def own_profile(self) -> dict:
        user_id = self._own_user_id()
        data = self.get(f"/user/profile/basic/{user_id}")
        return data.get("profile", data) if isinstance(data, dict) else data
