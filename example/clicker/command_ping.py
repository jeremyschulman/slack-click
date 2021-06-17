from random import randrange

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click
from slack_bolt.request.async_request import AsyncBoltRequest as Request
from slack_click.async_click import click_async, AsyncSlackClickCommand

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .app_data import app

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@click.command(name="/ping", cls=AsyncSlackClickCommand)
@click_async
@click.pass_obj
async def cli_ping_command(request: Request):
    say = request.context["say"]
    await say(f"Hiya <@{request.context.user_id}>.  Ping back at you :eyes:")


@app.command(cli_ping_command.name)
async def on_ping(request: Request, ack):
    await ack()
    return await cli_ping_command(prog_name=cli_ping_command.name, obj=request)


# -----------------------------------------------------------------------------
# /fuzzy command to manifest an anminal
# -----------------------------------------------------------------------------


animals = [":smile_cat:", ":hear_no_evil:", ":unicorn_face:"]


@click.command(
    name="/fuzzy", cls=AsyncSlackClickCommand, slack_request=lambda obj: obj["here"]
)
@click_async
@click.pass_obj
async def cli_fuzzy_command(obj: dict):
    request = obj["here"]
    say = request.context["say"]
    this_animal = animals[randrange(len(animals))]

    await say(f"Poof :magic_wand: {this_animal}")


@app.command(cli_fuzzy_command.name)
async def on_fuzzy(request: Request, ack):
    await ack()
    return await cli_fuzzy_command(
        prog_name=cli_fuzzy_command.name, obj={"here": request}
    )
