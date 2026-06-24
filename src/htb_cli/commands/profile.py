import typer
from rich import box
from rich.table import Table

from htb_cli.api import HTBClient
from htb_cli.commands._shared import JSON_OPTION, console, handle_api_errors, print_json

app = typer.Typer()


@app.command()
@handle_api_errors
def profile(as_json: bool = JSON_OPTION) -> None:
    """Show your own HTB profile."""
    client = HTBClient()
    info = client.own_profile()

    if as_json:
        print_json(info)
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
        ("ID", "id", None),
        ("Rank", "rank", None),
        ("Ranking", "ranking", None),
        ("Points", "points", None),
        ("User owns", "user_owns", None),
        ("System owns", "system_owns", None),
        ("User bloods", "user_bloods", None),
        ("System bloods", "system_bloods", None),
        ("Team", "team", None),
        ("Country", "country_name", None),
        ("University", "university_name", None),
    ]
    for label, key, formatter in fields:
        if key in info:
            value = info.get(key, "")
            table.add_row(label, formatter(value) if formatter else str(value))

    console.print(table)
