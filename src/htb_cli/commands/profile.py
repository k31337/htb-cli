import typer

from htb_cli.api import HTBClient
from htb_cli.commands._shared import (
    JSON_OPTION,
    build_detail_panel,
    console,
    handle_api_errors,
    points_text,
    print_json,
)

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

    field_specs = [
        ("ID", "id", None),
        ("Rank", "rank", None),
        ("Ranking", "ranking", None),
        ("Points", "points", points_text),
        ("User owns", "user_owns", None),
        ("System owns", "system_owns", None),
        ("User bloods", "user_bloods", None),
        ("System bloods", "system_bloods", None),
        ("Team", "team", None),
        ("Country", "country_name", None),
        ("University", "university_name", None),
    ]
    fields = [
        (label, formatter(info[key]) if formatter else str(info[key]))
        for label, key, formatter in field_specs
        if key in info
    ]

    console.print(build_detail_panel(str(info.get("name", "Profile")), fields))
