from importlib.metadata import version as _package_version

import typer

from htb_cli.api import CONFIG_FILE, delete_token, save_token
from htb_cli.commands._shared import console

app = typer.Typer()


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
