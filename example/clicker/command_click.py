import click

from slack_bolt.request.async_request import AsyncBoltRequest as Request
from slack_click import SlackClickGroup, version_option

from .app_data import slack_commands


# @slack_app.event("app_mention")
# async def handle_mentions(event, client, say):  # async function
#     api_response = await client.reactions_add(
#         channel=event["channel"],
#         timestamp=event["ts"],
#         name="eyes",
#     )
#
#     await say("What's up?")


@slack_commands.register()
@click.group(name="/click", cls=SlackClickGroup)
@version_option(version="0.1.0")
@click.pass_obj
async def cli_click_group(obj: dict):
    """
    This is the Clicker /click command group
    """
    request: Request = obj["request"]
    say = request.context["say"]
    await say("`/click` command invoked without any commands or options.")


@cli_click_group.command("ping")
@click.pass_obj
async def click_ping(obj):
    """Click ping"""
    request: Request = obj["request"]
    await request.context.say(":eyes: click-pong")
