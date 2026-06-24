import pytest

from htb_cli.api import HTBAPIError, HTBClient, delete_token, load_token, save_token


def test_load_token_returns_none_when_no_file():
    assert load_token() is None


def test_save_and_load_token_roundtrip():
    save_token("abc123")
    assert load_token() == "abc123"


def test_save_token_strips_whitespace():
    save_token("  abc123\n")
    assert load_token() == "abc123"


def test_delete_token_removes_file():
    save_token("abc123")
    assert delete_token() is True
    assert load_token() is None


def test_delete_token_when_nothing_saved():
    assert delete_token() is False


def test_client_uses_explicit_token():
    client = HTBClient(token="explicit-token")
    assert client.token == "explicit-token"


def test_client_uses_env_token(monkeypatch):
    monkeypatch.setenv("HTB_TOKEN", "  env-token  ")
    client = HTBClient()
    assert client.token == "env-token"


def test_client_uses_saved_token_when_no_env():
    save_token("saved-token")
    client = HTBClient()
    assert client.token == "saved-token"


def test_client_env_token_takes_priority_over_saved(monkeypatch):
    save_token("saved-token")
    monkeypatch.setenv("HTB_TOKEN", "env-token")
    client = HTBClient()
    assert client.token == "env-token"


def test_client_raises_without_any_token():
    with pytest.raises(HTBAPIError):
        HTBClient()
