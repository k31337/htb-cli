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
