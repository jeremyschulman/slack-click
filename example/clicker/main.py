# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import sys
from os import environ

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .app_data import api, app
from . import command_click  # noqa

# from . import command_ping

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

ENV_VARS = ["SLACK_APP_TOKEN", "SLACK_APP_PORT", "SLACK_BOT_TOKEN"]


@api.on_event("startup")
async def demo_startup():
    print("Starting Clicker ...")

    if missing := [envar for envar in ENV_VARS if not environ.get(envar)]:
        sys.exit(f"Missing required environment variables: {missing}")

    # start the websocket handler to consume messages from Slack
    await AsyncSocketModeHandler(app).start_async()
