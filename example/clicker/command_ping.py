from random import randrange

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click
from slack_click import SlackClickCommand, version_option
from slack_bolt.request.async_request import AsyncBoltRequest as Request

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .app_data import slack_commands

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

# Register the "/click" command with the Slack app for async-handling


@slack_commands.register()
@click.command(name="/ping", cls=SlackClickCommand)
@version_option(version="0.1.0")
@click.pass_obj
async def cli_ping_command(obj: dict):
    request: Request = obj["request"]
    say = request.context["say"]
    await say(f"Hiya <@{request.context.user_id}>.  Ping back at you :eyes:")


animals = [":smile_cat:", ":hear_no_evil:", ":unicorn_face:"]


@slack_commands.register()
@click.command(name="/fuzzy", cls=SlackClickCommand)
@click.pass_obj
async def cli_fuzzy_command(obj: dict):
    request: Request = obj["request"]
    say = request.context["say"]

    this_animal = animals[randrange(len(animals))]

    await say(f"Poof :magic_wand: {this_animal}")
