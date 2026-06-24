import typer
from rich import box
from rich.table import Table

from htb_cli.api import HTBClient
from htb_cli.commands._shared import JSON_OPTION, console, difficulty_text, handle_api_errors, paginate, print_json

app = typer.Typer()


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
            difficulty_text(challenge.get("difficulty", "")),
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
        print_json(items)
        return

    paginate(_build_challenges_table, items)


@app.command()
@handle_api_errors
def challenge(challenge_id: int, as_json: bool = JSON_OPTION) -> None:
    """Show details of a single challenge by ID."""
    client = HTBClient()
    info = client.challenge_profile(challenge_id)

    if as_json:
        print_json(info)
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
        ("Difficulty", "difficulty", difficulty_text),
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
