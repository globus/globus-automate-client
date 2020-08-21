import sys

import typer

from globus_automate_client import __version__
from globus_automate_client.cli import actions, flows, queues
from globus_automate_client.token_management import CONFIG_PATH

help = f"""
CLI for Globus Automate

By default, this CLI keeps all its config and cached tokens in {CONFIG_PATH}
"""

app = typer.Typer(help=help, short_help="Globus Automate CLI")
app.add_typer(actions.app, name="action")
app.add_typer(flows.app, name="flow")
app.add_typer(queues.app, name="queue")


def version_callback(display_version: bool):
    if display_version:
        typer.echo(f"globus-automate {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-V",
        callback=version_callback,
        help="Print CLI version number and exit",
        is_eager=True,
    ),
):
    pass


if __name__ == "__main__":
    app()
