import base64
import json
import os
import stat
from pathlib import Path

import httpx

BASE_URL = "https://labs.hackthebox.com/api/v4"
CONFIG_DIR = Path.home() / ".htb-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"


class HTBAPIError(Exception):
    pass


def save_token(token: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps({"token": token.strip()}))
    if os.name != "nt":
        os.chmod(CONFIG_FILE, stat.S_IRUSR | stat.S_IWUSR)


def load_token() -> str | None:
    if not CONFIG_FILE.exists():
        return None
    try:
        token = json.loads(CONFIG_FILE.read_text()).get("token")
        return token.strip() if token else None
    except (json.JSONDecodeError, OSError):
        return None


def delete_token() -> bool:
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
        return True
    return False


class HTBClient:
    def __init__(self, token: str | None = None) -> None:
        self.token = (token or os.environ.get("HTB_TOKEN") or load_token() or "").strip() or None
        if not self.token:
            raise HTBAPIError(
                "HTB token not found. Run 'htb login' or set the HTB_TOKEN environment variable."
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

    MAX_PAGES = 200

    def get_all_pages(self, path: str) -> list[dict]:
        items: list[dict] = []
        page = 1
        while page <= self.MAX_PAGES:
            data = self.get(path, params={"page": page})
            items.extend(data.get("data", []))
            last_page = data.get("meta", {}).get("last_page", page)
            if page >= last_page:
                break
            page += 1
        return items

    def active_machines(self) -> list[dict]:
        return self.get_all_pages("/machine/paginated")

    def retired_machines(self) -> list[dict]:
        return self.get_all_pages("/machine/list/retired/paginated")

    def machine_profile(self, id_or_name: str) -> dict:
        data = self.get(f"/machine/profile/{id_or_name}")
        return data.get("info", data) if isinstance(data, dict) else data

    def challenges(self) -> list[dict]:
        data = self.get("/challenge/list")
        return data.get("challenges", data) if isinstance(data, dict) else data

    def own_profile(self) -> dict:
        user_id = self._own_user_id()
        data = self.get(f"/user/profile/basic/{user_id}")
        return data.get("profile", data) if isinstance(data, dict) else data
