import functools
import math
import os
from importlib.metadata import version as _package_version
from typing import Callable

import click
import httpx
import typer
from rich import box
from rich.console import Console
from rich.table import Table

from htb_cli.api import CONFIG_FILE, HTBAPIError, HTBClient, delete_token, save_token

app = typer.Typer(help="Unofficial CLI to query the Hack The Box API")
console = Console()

PAGE_SIZE = 15

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


JSON_OPTION = typer.Option(False, "--json", help="Output raw JSON instead of a formatted table.")


def _print_json(value) -> None:
    console.print_json(data=value)


def _paginate(build_table: Callable[[list[dict]], Table], items: list[dict]) -> None:
    """Render items in pages of PAGE_SIZE, letting the user step through with n/p/q."""
    total_pages = max(1, math.ceil(len(items) / PAGE_SIZE))
    page = 1

    while True:
        start = (page - 1) * PAGE_SIZE
        chunk = items[start : start + PAGE_SIZE]

        os.system("cls" if os.name == "nt" else "clear")
        console.print(build_table(chunk))

        if total_pages <= 1:
            break

        console.print(f"[dim]Page {page}/{total_pages} -- n: next, p: previous, q: quit[/dim]")
        try:
            key = click.getchar()
        except (KeyboardInterrupt, EOFError):
            break

        if key in ("n", "N") and page < total_pages:
            page += 1
        elif key in ("p", "P") and page > 1:
            page -= 1
        elif key in ("q", "Q", "\x1b", "\x03"):
            break


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


@app.command()
def login() -> None:
    """Save your HTB API token so you don't have to set HTB_TOKEN every time."""
    token = typer.prompt("HTB API token", hide_input=True)
    save_token(token)
    console.print(f"[green]Token saved to {CONFIG_FILE}[/green]")


@app.command()
def logout() -> None:
    """Remove the saved HTB API token."""
    if delete_token():
        console.print("[green]Token removed.[/green]")
    else:
        console.print("[yellow]No saved token found.[/yellow]")


def _build_machines_table(title: str, items: list[dict]) -> Table:
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
        _print_json(items)
        return

    title = "Retired machines" if retired else "Active machines"
    _paginate(lambda chunk: _build_machines_table(title, chunk), items)


@app.command()
@handle_api_errors
def machine(id_or_name: str, as_json: bool = JSON_OPTION) -> None:
    """Show details of a single machine by ID or name."""
    client = HTBClient()
    info = client.machine_profile(id_or_name)

    if as_json:
        _print_json(info)
        return

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


def _build_challenges_table(items: list[dict]) -> Table:
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
            str(challenge.get("category_name", "")),
            _difficulty_text(challenge.get("difficulty", "")),
            str(challenge.get("points", "")),
        )

    return table


@app.command()
@handle_api_errors
def challenges(as_json: bool = JSON_OPTION) -> None:
    """List challenges on HTB."""
    client = HTBClient()
    items = client.challenges()

    if as_json:
        _print_json(items)
        return

    _paginate(_build_challenges_table, items)


@app.command()
@handle_api_errors
def challenge(challenge_id: int, as_json: bool = JSON_OPTION) -> None:
    """Show details of a single challenge by ID."""
    client = HTBClient()
    info = client.challenge_profile(challenge_id)

    if as_json:
        _print_json(info)
        return

    table = Table(
        title=str(info.get("name", challenge_id)),
        box=box.ROUNDED,
        title_style="bold green",
        show_header=False,
    )
    table.add_column("Field", style="bold cyan")
    table.add_column("Value")

    fields = [
        ("ID", "id", None),
        ("Category", "category_name", None),
        ("Difficulty", "difficulty", _difficulty_text),
        ("Points", "points", None),
        ("Solves", "solves", None),
        ("Rating", "rating", None),
        ("Retired", "retired", None),
        ("Release date", "release_date", None),
    ]
    for label, key, formatter in fields:
        if key in info:
            value = info.get(key, "")
            table.add_row(label, formatter(value) if formatter else str(value))

    console.print(table)


@app.command()
@handle_api_errors
def profile(as_json: bool = JSON_OPTION) -> None:
    """Show your own HTB profile."""
    client = HTBClient()
    info = client.own_profile()

    if as_json:
        _print_json(info)
        return

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
