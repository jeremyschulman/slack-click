import sys
from os import environ

from .app_data import api  # noqa
from . import api_slack  # noqa
from . import command_click  # noqa


ENV_VARS = ["SLACK_SIGNING_SECRET", "SLACK_BOT_TOKEN", "SLACK_APP_PORT"]

if __name__ == "__main__":
    if not all(environ.get(envar) for envar in ENV_VARS):
        sys.exit(f"Missing required environment variables: {ENV_VARS}")
