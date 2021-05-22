import sys
from os import environ

from fastapi import FastAPI, Request
from slack_sdk.web.async_client import AsyncWebClient
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.context.ack.async_ack import AsyncAck
from slack_bolt.context.say.async_say import AsyncSay
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.context.async_context import AsyncBoltContext

ENV_VARS = ['SLACK_SIGNING_SECRET', 'SLACK_BOT_TOKEN', 'SLACK_APP_PORT']

slack_app = AsyncApp()
slack_app_handler = AsyncSlackRequestHandler(slack_app)
api = FastAPI()


@slack_app.event("app_mention")
async def handle_mentions(event, client, say):  # async function
    api_response = await client.reactions_add(
        channel=event["channel"],
        timestamp=event["ts"],
        name="eyes",
    )

    await say("What's up?")


@slack_app.command('/click')
async def command_click(
    ack: AsyncAck, say: AsyncSay,
    client: AsyncWebClient,
    context: AsyncBoltContext,
    command: dict, request: AsyncBoltRequest
):
    await ack()
    await say(":eyes: Click called")


# -----------------------------------------------------------------------------
#
#                       FastAPI Routes for Slack endpoints
#
# -----------------------------------------------------------------------------

@api.post("/slack/command/{name}")
async def slack_command_endpoint(req: Request):
    return await slack_app_handler.handle(req)


@api.post("/slack/events")
async def slack_events_endpoint(req: Request):
    return await slack_app_handler.handle(req)


if __name__ == "__main__":
    if not all(environ.get(envar) for envar in ENV_VARS):
        sys.exit(f"Missing required environment variables: {ENV_VARS}")
