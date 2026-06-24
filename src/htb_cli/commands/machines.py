import time

import typer
from rich.table import Table

from htb_cli.api import HTBClient
from htb_cli.commands._shared import (
    JSON_OPTION,
    build_detail_panel,
    build_listing_table,
    console,
    difficulty_text,
    handle_api_errors,
    os_text,
    paginate,
    points_text,
    print_json,
)

app = typer.Typer()

SPAWN_POLL_SECONDS = 5
SPAWN_TIMEOUT_SECONDS = 180


def _build_machines_table(title: str, items: list[dict]) -> Table:
    table = build_listing_table(
        title,
        [
            ("ID", {"justify": "right", "style": "dim"}),
            ("Name", {"style": "bold"}),
            ("OS", {}),
            ("Difficulty", {}),
            ("Points", {"justify": "right"}),
        ],
    )

    for machine in items:
        table.add_row(
            str(machine.get("id", "")),
            str(machine.get("name", "")),
            os_text(machine.get("os", "")),
            difficulty_text(machine.get("difficultyText", "")),
            points_text(machine.get("points", "")),
        )

    return table


@app.command()
@handle_api_errors
def machines(
    retired: bool = typer.Option(False, "--retired", help="List retired machines instead of active ones."),
    as_json: bool = JSON_OPTION,
) -> None:
    """List active or retired machines on HTB."""
    client = HTBClient()
    items = client.retired_machines() if retired else client.active_machines()

    if as_json:
        print_json(items)
        return

    title = "Retired machines" if retired else "Active machines"
    paginate(lambda chunk: _build_machines_table(title, chunk), items)


@app.command()
@handle_api_errors
def machine(id_or_name: str, as_json: bool = JSON_OPTION) -> None:
    """Show details of a single machine by ID or name."""
    client = HTBClient()
    info = client.machine_profile(id_or_name)

    if as_json:
        print_json(info)
        return

    field_specs = [
        ("ID", "id", None),
        ("OS", "os", os_text),
        ("Difficulty", "difficultyText", difficulty_text),
        ("Points", "points", points_text),
        ("IP", "ip", None),
        ("Maker", "makerName", None),
        ("Rating", "stars", None),
        ("User owns", "userOwnsCount", None),
        ("Root owns", "rootOwnsCount", None),
        ("Retired", "retired", None),
        ("Release", "release", None),
    ]
    fields = [
        (label, formatter(info[key]) if formatter else str(info[key]))
        for label, key, formatter in field_specs
        if key in info
    ]

    console.print(build_detail_panel(str(info.get("name", id_or_name)), fields))


@app.command()
@handle_api_errors
def spawn(machine_id: int) -> None:
    """Spawn a machine and wait for its IP to be ready."""
    client = HTBClient()
    client.spawn_machine(machine_id)
    console.print(f"[green]Spawning machine {machine_id}...[/green]")

    elapsed = 0
    with console.status("Waiting for the machine to be ready..."):
        while elapsed < SPAWN_TIMEOUT_SECONDS:
            info = client.active_machine()
            if info and info.get("ip"):
                console.print(f"[bold green]IP:[/bold green] {info['ip']}")
                return
            time.sleep(SPAWN_POLL_SECONDS)
            elapsed += SPAWN_POLL_SECONDS

    console.print("[yellow]Timed out waiting for an IP. Check 'htb machine <id>' or the HTB website.[/yellow]")


@app.command()
@handle_api_errors
def stop(machine_id: int) -> None:
    """Stop the currently active machine."""
    client = HTBClient()
    client.stop_machine(machine_id)
    console.print(f"[green]Machine {machine_id} stopped.[/green]")


@app.command()
@handle_api_errors
def reset(machine_id: int) -> None:
    """Reset the active machine."""
    client = HTBClient()
    result = client.reset_machine(machine_id)
    message = result.get("message", "Reset requested.")
    console.print(f"[green]{message}[/green]")


@app.command()
@handle_api_errors
def submit(
    machine_id: int,
    flag: str,
    difficulty: int = typer.Option(50, "--difficulty", help="Your difficulty rating (1-100)."),
) -> None:
    """Submit a user/root flag for a machine."""
    client = HTBClient()
    result = client.submit_flag(machine_id, flag, difficulty)
    message = result.get("message", "Flag submitted.")
    console.print(f"[bold green]{message}[/bold green]")
