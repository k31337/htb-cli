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

app = typer.Typer(help="Browse HTB Seasons.")


@app.command(name="list")
@handle_api_errors
def list_seasons(as_json: bool = JSON_OPTION) -> None:
    """List all HTB Seasons."""
    client = HTBClient()
    items = client.seasons()

    if as_json:
        print_json(items)
        return

    table = build_listing_table(
        "Seasons",
        [
            ("ID", {"justify": "right", "style": "dim"}),
            ("Name", {"style": "bold"}),
            ("State", {}),
            ("Active", {}),
            ("Start date", {}),
        ],
    )
    for season in items:
        active = "[green]yes[/green]" if season.get("active") else "no"
        table.add_row(
            str(season.get("id", "")),
            str(season.get("name", "")),
            str(season.get("state", "")),
            active,
            str(season.get("start_date", "")),
        )

    console.print(table)


def _build_season_machines_table(items: list[dict]) -> Table:
    table = build_listing_table(
        "Season machines",
        [
            ("ID", {"justify": "right", "style": "dim"}),
            ("Name", {"style": "bold"}),
            ("OS", {}),
            ("Difficulty", {}),
            ("Points", {"justify": "right"}),
        ],
    )
    for machine in items:
        if machine.get("unknown"):
            continue
        points = machine.get("user_points", 0) + machine.get("root_points", 0)
        table.add_row(
            str(machine.get("id", "")),
            str(machine.get("name", "")),
            os_text(machine.get("os", "")),
            difficulty_text(machine.get("difficulty_text", "")),
            points_text(points),
        )
    return table


@app.command()
@handle_api_errors
def machines(as_json: bool = JSON_OPTION) -> None:
    """List machines in the active season."""
    client = HTBClient()
    items = client.season_machines()

    if as_json:
        print_json(items)
        return

    paginate(_build_season_machines_table, items)


@app.command()
@handle_api_errors
def progress(as_json: bool = JSON_OPTION) -> None:
    """Show your progress in the active season."""
    client = HTBClient()
    current = client.current_season()

    if not current:
        console.print("[yellow]No active season right now.[/yellow]")
        return

    info = client.season_progress(current["id"])
    if not info:
        console.print(f"[yellow]No progress yet for {current.get('name', 'this season')}.[/yellow]")
        return

    if as_json:
        print_json(info)
        return

    rank = info.get("rank", {})
    owns = info.get("owns", {})
    fields = [
        ("Tier", str(info.get("season", {}).get("tier", ""))),
        ("Rank", f"{rank.get('current', '')}{rank.get('suffix', '')} / {rank.get('total', '')}"),
        ("User flags", str(owns.get("user", {}).get("flags_pawned", ""))),
        ("User bloods", str(owns.get("user", {}).get("bloods_obtained", ""))),
        ("Root flags", str(owns.get("root", {}).get("flags_pawned", ""))),
        ("Root bloods", str(owns.get("root", {}).get("bloods_obtained", ""))),
        ("Total machines", str(owns.get("total_machines", ""))),
    ]
    console.print(build_detail_panel(current.get("name", "Season progress"), fields))
