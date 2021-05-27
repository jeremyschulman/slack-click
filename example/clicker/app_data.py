# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from fastapi import FastAPI
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_click.app_click import SlackAppCommands

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["api", "slack_app", "slack_commands", "slack_socket_handler"]

# -----------------------------------------------------------------------------
#                                 GLOBALS
# -----------------------------------------------------------------------------

api = FastAPI()
slack_app = AsyncApp()
slack_socket_handler = AsyncSocketModeHandler(slack_app)
slack_commands = SlackAppCommands(app=slack_app)
