import functools
import math
import os
from typing import Callable

import click
import httpx
import typer
from rich.console import Console
from rich.table import Table

from htb_cli.api import HTBAPIError

console = Console()

PAGE_SIZE = 15

DIFFICULTY_COLORS = {
    "easy": "green",
    "medium": "yellow",
    "hard": "red",
    "insane": "magenta",
}

JSON_OPTION = typer.Option(False, "--json", help="Output raw JSON instead of a formatted table.")


def difficulty_text(difficulty: str) -> str:
    color = DIFFICULTY_COLORS.get(str(difficulty).lower())
    return f"[{color}]{difficulty}[/{color}]" if color else str(difficulty)


def os_text(os_name: str) -> str:
    return "[cyan]" + str(os_name) + "[/cyan]"


def print_json(value: dict | list) -> None:
    console.print_json(data=value)


def paginate(build_table: Callable[[list[dict]], Table], items: list[dict]) -> None:
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
