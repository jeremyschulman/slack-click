# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import sys
from os import environ

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .app_data import api  # noqa
from . import api_slack  # noqa
from . import command_click  # noqa

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

ENV_VARS = ["SLACK_SIGNING_SECRET", "SLACK_BOT_TOKEN", "SLACK_APP_PORT"]


@api.on_event("startup")
async def demo_startup():
    if missing := [envar for envar in ENV_VARS if not environ.get(envar)]:
        sys.exit(f"Missing required environment variables: {missing}")
