import typer

from htb_cli.commands import auth, challenges, machines, profile, vpn

app = typer.Typer(help="Unofficial CLI to query the Hack The Box API")

for module in (auth, machines, challenges, profile):
    app.registered_commands += module.app.registered_commands

app.add_typer(vpn.app, name="vpn")


if __name__ == "__main__":
    app()
