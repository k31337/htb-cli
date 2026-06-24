import functools

import httpx
import typer
from rich.console import Console
from rich.table import Table

from htb_cli.api import HTBAPIError, HTBClient

app = typer.Typer(help="Unofficial CLI to query the Hack The Box API")
console = Console()


def handle_api_errors(func):
    """Catch HTB API errors and print them consistently before exiting."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTBAPIError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1)
        except httpx.HTTPStatusError as exc:
            console.print(f"[red]HTTP error:[/red] {exc}")
            raise typer.Exit(code=1)

    return wrapper


@app.command()
def version() -> None:
    """Show the CLI version."""
    console.print("htb-cli 0.1.0")


def _print_machines_table(title: str, items: list[dict]) -> None:
    table = Table(title=title)
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("OS")
    table.add_column("Difficulty")
    table.add_column("Points")

    for machine in items:
        table.add_row(
            str(machine.get("id", "")),
            str(machine.get("name", "")),
            str(machine.get("os", "")),
            str(machine.get("difficultyText", "")),
            str(machine.get("points", "")),
        )

    console.print(table)


@app.command()
@handle_api_errors
def machines(
    retired: bool = typer.Option(False, "--retired", help="List retired machines instead of active ones."),
) -> None:
    """List active or retired machines on HTB."""
    client = HTBClient()
    items = client.retired_machines() if retired else client.active_machines()

    title = "Retired machines" if retired else "Active machines"
    _print_machines_table(title, items)


@app.command()
@handle_api_errors
def machine(id_or_name: str) -> None:
    """Show details of a single machine by ID or name."""
    client = HTBClient()
    info = client.machine_profile(id_or_name)

    table = Table(title=str(info.get("name", id_or_name)), show_header=False)
    table.add_column("Field", style="bold")
    table.add_column("Value")

    fields = [
        ("ID", "id"),
        ("OS", "os"),
        ("Difficulty", "difficultyText"),
        ("Points", "points"),
        ("IP", "ip"),
        ("Maker", "makerName"),
        ("Rating", "stars"),
        ("User owns", "userOwnsCount"),
        ("Root owns", "rootOwnsCount"),
        ("Retired", "retired"),
        ("Release", "release"),
    ]
    for label, key in fields:
        if key in info:
            table.add_row(label, str(info.get(key, "")))

    console.print(table)


@app.command()
@handle_api_errors
def profile() -> None:
    """Show your own HTB profile."""
    client = HTBClient()
    info = client.own_profile()

    table = Table(title=str(info.get("name", "Profile")), show_header=False)
    table.add_column("Field", style="bold")
    table.add_column("Value")

    fields = [
        ("ID", "id"),
        ("Rank", "rank"),
        ("Ranking", "ranking"),
        ("Points", "points"),
        ("User owns", "user_owns"),
        ("System owns", "system_owns"),
        ("User bloods", "user_bloods"),
        ("System bloods", "system_bloods"),
        ("Team", "team"),
        ("Country", "country_name"),
        ("University", "university_name"),
    ]
    for label, key in fields:
        if key in info:
            table.add_row(label, str(info.get(key, "")))

    console.print(table)


if __name__ == "__main__":
    app()
