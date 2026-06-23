import httpx
import typer
from rich.console import Console
from rich.table import Table

from htb_cli.api import HTBAPIError, HTBClient

app = typer.Typer(help="Unofficial CLI to query the Hack The Box API")
console = Console()


@app.command()
def version() -> None:
    """Show the CLI version."""
    console.print("htb-cli 0.1.0")


@app.command()
def machines() -> None:
    """List active machines on HTB."""
    try:
        client = HTBClient()
        items = client.active_machines()
    except HTBAPIError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)
    except httpx.HTTPStatusError as exc:
        console.print(f"[red]HTTP error:[/red] {exc}")
        raise typer.Exit(code=1)

    table = Table(title="Active machines")
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


if __name__ == "__main__":
    app()
