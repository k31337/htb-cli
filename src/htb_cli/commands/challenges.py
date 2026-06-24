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
    paginate,
    points_text,
    print_json,
)

app = typer.Typer()


def _build_challenges_table(items: list[dict]) -> Table:
    table = build_listing_table(
        "Challenges",
        [
            ("ID", {"justify": "right", "style": "dim"}),
            ("Name", {"style": "bold"}),
            ("Category", {}),
            ("Difficulty", {}),
            ("Points", {"justify": "right"}),
        ],
    )

    for challenge in items:
        table.add_row(
            str(challenge.get("id", "")),
            str(challenge.get("name", "")),
            str(challenge.get("category_name", "")),
            difficulty_text(challenge.get("difficulty", "")),
            points_text(challenge.get("points", "")),
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

    field_specs = [
        ("ID", "id", None),
        ("Category", "category_name", None),
        ("Difficulty", "difficulty", difficulty_text),
        ("Points", "points", points_text),
        ("Solves", "solves", None),
        ("Rating", "rating", None),
        ("Retired", "retired", None),
        ("Release date", "release_date", None),
    ]
    fields = [
        (label, formatter(info[key]) if formatter else str(info[key]))
        for label, key, formatter in field_specs
        if key in info
    ]

    console.print(build_detail_panel(str(info.get("name", challenge_id)), fields))
