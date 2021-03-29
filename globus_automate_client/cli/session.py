import json

import typer

from globus_automate_client.cli.auth import get_current_user, logout, revoke_login
from globus_automate_client.cli.helpers import verbosity_option

app = typer.Typer(short_help="Manage your session with the Automate Command Line")


@app.command("whoami")
def session_whoami(verbose: bool = verbosity_option):
    """
    Determine the username for the identity logged in to Globus Auth.
    If run with increased verbosity, the caller's full user information is
    displayed.
    """
    user = get_current_user()
    if verbose:
        output = json.dumps(user, indent=2)
    else:
        output = user["preferred_username"]
    typer.secho(output, fg=typer.colors.GREEN)


@app.command("logout")
def session_logout():
    """
    Remove all locally cached Globus Automate authentication information.
    """
    logout()
    typer.secho("Logged Out", fg=typer.colors.GREEN)


@app.command("revoke")
def session_revoke():
    """
    Remove all locally cached Globus Automate authentication information and
    invalidate all locally cached access or refresh tokens. These tokens can no
    longer be used elsewhere.
    """
    revoke_login()
    typer.secho("All stored consents have been revoked", fg=typer.colors.GREEN)
