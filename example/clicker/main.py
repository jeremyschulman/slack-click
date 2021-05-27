# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import sys
from os import environ

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .app_data import api, slack_socket_handler  # noqa
from . import command_click  # noqa
from . import command_ping  # noqa

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

ENV_VARS = ["SLACK_SIGNING_SECRET", "SLACK_APP_TOKEN", "SLACK_APP_PORT"]


@api.on_event("startup")
async def demo_startup():
    if missing := [envar for envar in ENV_VARS if not environ.get(envar)]:
        sys.exit(f"Missing required environment variables: {missing}")

    # start the websocket handler to consume messages from Slack
    await slack_socket_handler.start_async()
