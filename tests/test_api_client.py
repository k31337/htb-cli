import httpx
import pytest
import respx

from htb_cli.api import BASE_URL, HTBAPIError, HTBClient


@pytest.fixture
def client(fake_token) -> HTBClient:
    return HTBClient(token=fake_token)


@respx.mock
def test_get_handles_401(client):
    respx.get(f"{BASE_URL}/machine/active").mock(return_value=httpx.Response(401))
    with pytest.raises(HTBAPIError, match="Invalid or expired token"):
        client.get("/machine/active")


@respx.mock
def test_get_handles_404(client):
    respx.get(f"{BASE_URL}/machine/profile/999999").mock(return_value=httpx.Response(404))
    with pytest.raises(HTBAPIError, match="Not found"):
        client.machine_profile(999999)


@respx.mock
def test_post_handles_400_with_message(client):
    respx.post(f"{BASE_URL}/vm/spawn").mock(
        return_value=httpx.Response(400, json={"message": "You already have an active machine."})
    )
    with pytest.raises(HTBAPIError, match="You already have an active machine."):
        client.spawn_machine(912)


@respx.mock
def test_get_all_pages_collects_every_page(client):
    respx.get(f"{BASE_URL}/machine/paginated", params={"page": "1"}).mock(
        return_value=httpx.Response(200, json={"data": [{"id": 1}, {"id": 2}], "meta": {"last_page": 2}})
    )
    respx.get(f"{BASE_URL}/machine/paginated", params={"page": "2"}).mock(
        return_value=httpx.Response(200, json={"data": [{"id": 3}], "meta": {"last_page": 2}})
    )

    items = client.active_machines()

    assert [item["id"] for item in items] == [1, 2, 3]


@respx.mock
def test_get_all_pages_handles_null_meta(client):
    respx.get(f"{BASE_URL}/machine/paginated", params={"page": "1"}).mock(
        return_value=httpx.Response(200, json={"data": [{"id": 1}], "meta": None})
    )

    items = client.active_machines()

    assert items == [{"id": 1}]


@respx.mock
def test_machine_profile_unwraps_info(client):
    respx.get(f"{BASE_URL}/machine/profile/912").mock(
        return_value=httpx.Response(200, json={"info": {"id": 912, "name": "Nimbus"}})
    )

    info = client.machine_profile(912)

    assert info == {"id": 912, "name": "Nimbus"}


@respx.mock
def test_challenges_resolves_category_name(client):
    respx.get(f"{BASE_URL}/challenge/list").mock(
        return_value=httpx.Response(
            200,
            json={"challenges": [{"id": 59, "name": "Cryptohorrific", "challenge_category_id": 8}]},
        )
    )
    respx.get(f"{BASE_URL}/challenge/categories/list").mock(
        return_value=httpx.Response(200, json={"info": [{"id": 8, "name": "Crypto"}]})
    )

    items = client.challenges()

    assert items[0]["category_name"] == "Crypto"


@respx.mock
def test_challenge_profile_resolves_category(client):
    respx.get(f"{BASE_URL}/challenge/info/59").mock(
        return_value=httpx.Response(
            200, json={"challenge": {"id": 59, "name": "Cryptohorrific", "challenge_category_id": 8}}
        )
    )
    respx.get(f"{BASE_URL}/challenge/categories/list").mock(
        return_value=httpx.Response(200, json={"info": [{"id": 8, "name": "Crypto"}]})
    )

    info = client.challenge_profile(59)

    assert info["category_name"] == "Crypto"


@respx.mock
def test_own_profile_uses_jwt_subject(client):
    respx.get(f"{BASE_URL}/user/profile/basic/123").mock(
        return_value=httpx.Response(200, json={"profile": {"id": 123, "name": "k31337"}})
    )

    info = client.own_profile()

    assert info == {"id": 123, "name": "k31337"}


@respx.mock
def test_spawn_machine_posts_machine_id(client):
    route = respx.post(f"{BASE_URL}/vm/spawn").mock(
        return_value=httpx.Response(200, json={"message": "Playing machine."})
    )

    result = client.spawn_machine(912)

    assert route.calls.last.request.content == b'{"machine_id":912}'
    assert result["message"] == "Playing machine."


@respx.mock
def test_submit_flag_posts_expected_body(client):
    route = respx.post(f"{BASE_URL}/machine/own").mock(
        return_value=httpx.Response(200, json={"message": "Congrats! You have owned root!"})
    )

    result = client.submit_flag(912, "flag{test}", difficulty=70)

    sent = route.calls.last.request.content
    assert b'"id":912' in sent
    assert b'"flag":"flag{test}"' in sent
    assert b'"difficulty":70' in sent
    assert "Congrats" in result["message"]
