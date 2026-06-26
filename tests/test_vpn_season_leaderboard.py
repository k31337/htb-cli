import httpx
import pytest
import respx

from htb_cli.api import BASE_URL, V5_BASE_URL, HTBClient


@pytest.fixture
def client(fake_token) -> HTBClient:
    return HTBClient(token=fake_token)


# --- VPN -----------------------------------------------------------------


@respx.mock
def test_vpn_status_returns_assigned_labs_server(client):
    respx.get(f"{V5_BASE_URL}/connections").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {"type": "starting_point", "assigned_server": {"id": 412, "friendly_name": "SP 1"}},
                    {"type": "labs", "assigned_server": {"id": 698, "friendly_name": "EU Machines VIP+ 3"}},
                ]
            },
        )
    )

    server = client.vpn_status()

    assert server == {"id": 698, "friendly_name": "EU Machines VIP+ 3"}


@respx.mock
def test_vpn_status_returns_none_without_labs_connection(client):
    respx.get(f"{V5_BASE_URL}/connections").mock(return_value=httpx.Response(200, json={"data": []}))

    assert client.vpn_status() is None


@respx.mock
def test_vpn_servers_flattens_nested_locations(client):
    respx.get(f"{BASE_URL}/connections/servers", params={"product": "labs"}).mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "options": {
                        "EU": {
                            "EU - Free": {
                                "servers": {
                                    "1": {"id": 1, "friendly_name": "EU Free 1"},
                                    "201": {"id": 201, "friendly_name": "EU Free 2"},
                                }
                            }
                        },
                        "US": {"US - Free": {"servers": {"113": {"id": 113, "friendly_name": "US Free 1"}}}},
                    }
                }
            },
        )
    )

    servers = client.vpn_servers()

    assert {s["id"] for s in servers} == {1, 201, 113}


@respx.mock
def test_switch_vpn_server_posts_to_correct_id(client):
    route = respx.post(f"{BASE_URL}/connections/servers/switch/698").mock(
        return_value=httpx.Response(200, json={"message": "VPN Server switched"})
    )

    result = client.switch_vpn_server(698)

    assert route.called
    assert result["message"] == "VPN Server switched"


@respx.mock
def test_download_ovpn_uses_udp_by_default(client):
    route = respx.get(f"{BASE_URL}/access/ovpnfile/698/0").mock(return_value=httpx.Response(200, content=b"client\n"))

    content = client.download_ovpn(698)

    assert route.called
    assert content == b"client\n"


@respx.mock
def test_download_ovpn_appends_tcp_suffix(client):
    route = respx.get(f"{BASE_URL}/access/ovpnfile/698/0/1").mock(return_value=httpx.Response(200, content=b"proto tcp\n"))

    client.download_ovpn(698, tcp=True)

    assert route.called


# --- Seasons ---------------------------------------------------------------


@respx.mock
def test_current_season_picks_active_one(client):
    respx.get(f"{BASE_URL}/season/list").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {"id": 1, "name": "Season 1", "active": False},
                    {"id": 2, "name": "Season 2", "active": True},
                ]
            },
        )
    )

    current = client.current_season()

    assert current == {"id": 2, "name": "Season 2", "active": True}


@respx.mock
def test_season_machines_returns_data(client):
    respx.get(f"{BASE_URL}/season/machines").mock(
        return_value=httpx.Response(200, json={"data": [{"id": 900, "name": "Reactor"}, {"unknown": True}]})
    )

    machines = client.season_machines()

    assert len(machines) == 2


@respx.mock
def test_season_progress_returns_none_when_no_data(client):
    respx.get(f"{BASE_URL}/season/end/2/123").mock(return_value=httpx.Response(200, json={"data": None}))

    assert client.season_progress(2) is None


@respx.mock
def test_season_progress_returns_data(client):
    respx.get(f"{BASE_URL}/season/end/2/123").mock(
        return_value=httpx.Response(200, json={"data": {"rank": {"current": 5}}})
    )

    progress = client.season_progress(2)

    assert progress == {"rank": {"current": 5}}


# --- Leaderboard -------------------------------------------------------------


@respx.mock
def test_leaderboard_users_returns_data(client):
    respx.get(f"{BASE_URL}/rankings/users").mock(
        return_value=httpx.Response(200, json={"data": [{"rank": 1, "name": "xct"}]})
    )

    items = client.leaderboard_users()

    assert items == [{"rank": 1, "name": "xct"}]


@respx.mock
def test_leaderboard_teams_returns_data(client):
    respx.get(f"{BASE_URL}/rankings/teams").mock(
        return_value=httpx.Response(200, json={"data": [{"rank": 1, "name": "rpwn"}]})
    )

    items = client.leaderboard_teams()

    assert items == [{"rank": 1, "name": "rpwn"}]


@respx.mock
def test_leaderboard_universities_returns_data(client):
    respx.get(f"{BASE_URL}/rankings/universities").mock(
        return_value=httpx.Response(200, json={"data": [{"rank": 1, "students": 100}]})
    )

    items = client.leaderboard_universities()

    assert items == [{"rank": 1, "students": 100}]


@respx.mock
def test_leaderboard_country_unwraps_rankings(client):
    respx.get(f"{BASE_URL}/rankings/country/ES/members").mock(
        return_value=httpx.Response(
            200, json={"data": {"country_name": "Spain", "rankings": [{"rank": 1, "name": "blindma1den"}]}}
        )
    )

    items = client.leaderboard_country("ES")

    assert items == [{"rank": 1, "name": "blindma1den"}]
