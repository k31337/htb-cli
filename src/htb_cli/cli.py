import functools
from importlib.metadata import version as _package_version

import httpx
import typer
from rich import box
from rich.console import Console
from rich.table import Table

from htb_cli.api import HTBAPIError, HTBClient

app = typer.Typer(help="Unofficial CLI to query the Hack The Box API")
console = Console()

DIFFICULTY_COLORS = {
    "easy": "green",
    "medium": "yellow",
    "hard": "red",
    "insane": "magenta",
}


def _difficulty_text(difficulty: str) -> str:
    color = DIFFICULTY_COLORS.get(str(difficulty).lower())
    return f"[{color}]{difficulty}[/{color}]" if color else str(difficulty)


def _os_text(os_name: str) -> str:
    return "[cyan]" + str(os_name) + "[/cyan]"


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
    console.print(f"htb-cli {_package_version('htb-cli')}")


def _print_machines_table(title: str, items: list[dict]) -> None:
    table = Table(title=title, box=box.ROUNDED, title_style="bold green", header_style="bold")
    table.add_column("ID", justify="right", style="dim")
    table.add_column("Name", style="bold")
    table.add_column("OS")
    table.add_column("Difficulty")
    table.add_column("Points", justify="right")

    for machine in items:
        table.add_row(
            str(machine.get("id", "")),
            str(machine.get("name", "")),
            _os_text(machine.get("os", "")),
            _difficulty_text(machine.get("difficultyText", "")),
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

    table = Table(
        title=str(info.get("name", id_or_name)),
        box=box.ROUNDED,
        title_style="bold green",
        show_header=False,
    )
    table.add_column("Field", style="bold cyan")
    table.add_column("Value")

    fields = [
        ("ID", "id", None),
        ("OS", "os", _os_text),
        ("Difficulty", "difficultyText", _difficulty_text),
        ("Points", "points", None),
        ("IP", "ip", None),
        ("Maker", "makerName", None),
        ("Rating", "stars", None),
        ("User owns", "userOwnsCount", None),
        ("Root owns", "rootOwnsCount", None),
        ("Retired", "retired", None),
        ("Release", "release", None),
    ]
    for label, key, formatter in fields:
        if key in info:
            value = info.get(key, "")
            table.add_row(label, formatter(value) if formatter else str(value))

    console.print(table)


@app.command()
@handle_api_errors
def challenges() -> None:
    """List challenges on HTB."""
    client = HTBClient()
    items = client.challenges()

    table = Table(title="Challenges", box=box.ROUNDED, title_style="bold green", header_style="bold")
    table.add_column("ID", justify="right", style="dim")
    table.add_column("Name", style="bold")
    table.add_column("Category")
    table.add_column("Difficulty")
    table.add_column("Points", justify="right")

    for challenge in items:
        table.add_row(
            str(challenge.get("id", "")),
            str(challenge.get("name", "")),
            str(challenge.get("challenge_category", challenge.get("category_name", ""))),
            _difficulty_text(challenge.get("difficulty", "")),
            str(challenge.get("points", "")),
        )

    console.print(table)


@app.command()
@handle_api_errors
def profile() -> None:
    """Show your own HTB profile."""
    client = HTBClient()
    info = client.own_profile()

    table = Table(
        title=str(info.get("name", "Profile")),
        box=box.ROUNDED,
        title_style="bold green",
        show_header=False,
    )
    table.add_column("Field", style="bold cyan")
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
