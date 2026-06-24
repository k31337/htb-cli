import base64
import json

import pytest


def make_jwt(sub: str = "123") -> str:
    """Build a fake (unsigned) JWT with the given subject, like an HTB API token."""
    header = base64.urlsafe_b64encode(json.dumps({"alg": "RS256", "typ": "JWT"}).encode()).rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(json.dumps({"sub": sub}).encode()).rstrip(b"=").decode()
    return f"{header}.{payload}.fakesignature"


@pytest.fixture
def fake_token() -> str:
    return make_jwt("123")


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """Keep tests from touching the real ~/.htb-cli/config.json or the real HTB_TOKEN."""
    import htb_cli.api as api

    monkeypatch.setattr(api, "CONFIG_DIR", tmp_path / ".htb-cli")
    monkeypatch.setattr(api, "CONFIG_FILE", tmp_path / ".htb-cli" / "config.json")
    monkeypatch.delenv("HTB_TOKEN", raising=False)
