# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click
from slack_bolt.request.async_request import AsyncBoltRequest as Request
from slack_click.async_click import click_async, version_option, AsyncSlackClickGroup

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .app_data import app


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


# Register the "/click" command with the Slack app for async-handling


@click.group(name="/clicker", cls=AsyncSlackClickGroup)
@version_option(version="0.1.0")
@click.pass_obj
@click_async
async def cli_click_group(request: Request):
    """
    This is the Clicker /click command group
    """
    say = request.context["say"]
    await say("`/click` command invoked without any commands or options.")


@app.command(cli_click_group.name)
async def on_clicker(request: Request, ack, say):
    await ack()
    await say("Got it.")

    return await cli_click_group(prog_name=cli_click_group.name, obj=request)


@cli_click_group.command("hello")
@click.pass_obj
async def click_hello_command(request: Request):
    await request.context.say(f"Hi there <@{request.context.user_id}> :eyes:")


@cli_click_group.command("goodbye")
@click.option("--name", help="who dis?", required=True)
@click.pass_obj
async def click_goodby_command(request: Request, name: str):
    await request.context.say(f"Good-bye {name} :wave:")
