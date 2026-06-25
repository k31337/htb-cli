from pathlib import Path

import typer

from htb_cli.api import HTBClient
from htb_cli.commands._shared import (
    JSON_OPTION,
    build_detail_panel,
    build_listing_table,
    console,
    handle_api_errors,
    print_json,
)

app = typer.Typer(help="Manage your HTB VPN connection.")


@app.command()
@handle_api_errors
def status(as_json: bool = JSON_OPTION) -> None:
    """Show the VPN server currently assigned to your account."""
    client = HTBClient()
    server = client.vpn_status()

    if as_json:
        print_json(server or {})
        return

    if not server:
        console.print("[yellow]No VPN server assigned yet. Run 'htb vpn switch <id>' first.[/yellow]")
        return

    fields = [
        ("ID", str(server.get("id", ""))),
        ("Location", str(server.get("location", ""))),
        ("Clients", str(server.get("current_clients", ""))),
    ]
    console.print(build_detail_panel(str(server.get("friendly_name", "VPN server")), fields))


@app.command()
@handle_api_errors
def servers(as_json: bool = JSON_OPTION) -> None:
    """List available VPN servers."""
    client = HTBClient()
    items = client.vpn_servers()

    if as_json:
        print_json(items)
        return

    table = build_listing_table(
        "VPN servers",
        [
            ("ID", {"justify": "right", "style": "dim"}),
            ("Name", {"style": "bold"}),
            ("Location", {}),
            ("Clients", {"justify": "right"}),
        ],
    )
    for server in items:
        table.add_row(
            str(server.get("id", "")),
            str(server.get("friendly_name", "")),
            str(server.get("location", "")),
            str(server.get("current_clients", "")),
        )

    console.print(table)


@app.command()
@handle_api_errors
def switch(server_id: int) -> None:
    """Switch to a different VPN server."""
    client = HTBClient()
    result = client.switch_vpn_server(server_id)
    message = result.get("message", "VPN server switched.")
    console.print(f"[green]{message}[/green]")


@app.command()
@handle_api_errors
def download(
    server_id: int,
    tcp: bool = typer.Option(False, "--tcp", help="Download the TCP config instead of UDP."),
    output: Path = typer.Option(None, "-o", "--output", help="Where to save the .ovpn file."),
) -> None:
    """Download the .ovpn config file for a VPN server."""
    client = HTBClient()
    content = client.download_ovpn(server_id, tcp=tcp)

    destination = output or Path(f"htb-{server_id}.ovpn")
    destination.write_bytes(content)
    console.print(f"[green]Saved to {destination}[/green]")
