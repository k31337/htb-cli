import typer

from htb_cli.commands import auth, challenges, machines, profile

app = typer.Typer(help="Unofficial CLI to query the Hack The Box API")

for module in (auth, machines, challenges, profile):
    app.registered_commands += module.app.registered_commands


if __name__ == "__main__":
    app()
