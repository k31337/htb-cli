import typer
from rich.table import Table

from htb_cli.api import HTBClient
from htb_cli.commands._shared import (
    JSON_OPTION,
    build_listing_table,
    console,
    handle_api_errors,
    paginate,
    points_text,
    print_json,
)

app = typer.Typer(help="Browse HTB leaderboards.")


def _build_ranking_table(title: str, items: list[dict], extra_column: tuple[str, str] | None = None) -> Table:
    columns = [
        ("Rank", {"justify": "right", "style": "dim"}),
        ("Name", {"style": "bold"}),
        ("Country", {}),
    ]
    if extra_column:
        columns.append((extra_column[0], {"justify": "right"}))
    columns.append(("Points", {"justify": "right"}))

    table = build_listing_table(title, columns)

    for entry in items:
        row = [
            str(entry.get("rank", "")),
            str(entry.get("name", "")),
            str(entry.get("country", "")),
        ]
        if extra_column:
            row.append(str(entry.get(extra_column[1], "")))
        row.append(points_text(entry.get("points", "")))
        table.add_row(*row)

    return table


@app.command()
@handle_api_errors
def users(as_json: bool = JSON_OPTION) -> None:
    """Top 100 hackers worldwide."""
    client = HTBClient()
    items = client.leaderboard_users()

    if as_json:
        print_json(items)
        return

    paginate(lambda chunk: _build_ranking_table("Leaderboard - Users", chunk), items)


@app.command()
@handle_api_errors
def teams(as_json: bool = JSON_OPTION) -> None:
    """Top 100 teams worldwide."""
    client = HTBClient()
    items = client.leaderboard_teams()

    if as_json:
        print_json(items)
        return

    paginate(lambda chunk: _build_ranking_table("Leaderboard - Teams", chunk), items)


@app.command()
@handle_api_errors
def universities(as_json: bool = JSON_OPTION) -> None:
    """Top 100 universities worldwide."""
    client = HTBClient()
    items = client.leaderboard_universities()

    if as_json:
        print_json(items)
        return

    paginate(
        lambda chunk: _build_ranking_table("Leaderboard - Universities", chunk, extra_column=("Students", "students")),
        items,
    )


@app.command()
@handle_api_errors
def country(country_code: str, as_json: bool = JSON_OPTION) -> None:
    """Top 100 hackers for a given country code (e.g. ES, US, DE)."""
    client = HTBClient()
    items = client.leaderboard_country(country_code.upper())

    if not items:
        console.print(f"[yellow]No ranking data found for country '{country_code}'.[/yellow]")
        return

    if as_json:
        print_json(items)
        return

    paginate(lambda chunk: _build_ranking_table(f"Leaderboard - {country_code.upper()}", chunk), items)
