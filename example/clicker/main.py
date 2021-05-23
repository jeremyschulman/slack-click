import sys
from os import environ

from .app_data import api  # noqa
from . import api_slack  # noqa
from . import command_click  # noqa


ENV_VARS = ["SLACK_SIGNING_SECRET", "SLACK_BOT_TOKEN", "SLACK_APP_PORT"]

if missing := [envar for envar in ENV_VARS if not environ.get(envar)]:
    sys.exit(f"Missing required environment variables: {missing}")
