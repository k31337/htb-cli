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
    MAX_PAGES = 200

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
        return self._handle_response(response)

    def post(self, path: str, json_body: dict | None = None) -> dict:
        url = f"{BASE_URL}{path}"
        response = httpx.post(url, headers=self._headers(), json=json_body, timeout=15)
        return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> dict:
        if response.status_code == 401:
            raise HTBAPIError("Invalid or expired token.")
        if response.status_code == 404:
            raise HTBAPIError("Not found. Check the ID or name and try again.")
        if response.status_code == 400:
            message = response.json().get("message", "Bad request.") if response.content else "Bad request."
            raise HTBAPIError(message)
        response.raise_for_status()
        return response.json() if response.content else {}

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

    def challenge_categories(self) -> dict[int, str]:
        data = self.get("/challenge/categories/list")
        categories = data.get("info", data) if isinstance(data, dict) else data
        return {category["id"]: category["name"] for category in categories}

    def challenges(self) -> list[dict]:
        data = self.get("/challenge/list")
        items = data.get("challenges", data) if isinstance(data, dict) else data

        categories = self.challenge_categories()
        for item in items:
            item["category_name"] = categories.get(item.get("challenge_category_id"), "")

        return items

    def challenge_profile(self, challenge_id: int) -> dict:
        data = self.get(f"/challenge/info/{challenge_id}")
        info = data.get("challenge", data) if isinstance(data, dict) else data
        category_id = info.get("category_id", info.get("challenge_category_id"))
        if category_id is not None:
            info["category_name"] = self.challenge_categories().get(category_id, "")
        return info

    def spawn_machine(self, machine_id: int) -> dict:
        return self.post("/vm/spawn", json_body={"machine_id": machine_id})

    def stop_machine(self, machine_id: int) -> dict:
        return self.post("/vm/terminate", json_body={"machine_id": machine_id})

    def active_machine(self) -> dict | None:
        data = self.get("/machine/active")
        info = data.get("info", data) if isinstance(data, dict) else data
        return info or None

    def own_profile(self) -> dict:
        user_id = self._own_user_id()
        data = self.get(f"/user/profile/basic/{user_id}")
        return data.get("profile", data) if isinstance(data, dict) else data
