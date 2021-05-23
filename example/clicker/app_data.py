# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from fastapi import FastAPI
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_click.app_click import SlackAppCommands

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["api", "slack_app", "slack_app_handler", "slack_commands"]

# -----------------------------------------------------------------------------
#                                 GLOBALS
# -----------------------------------------------------------------------------

api = FastAPI()
slack_app = AsyncApp()
slack_app_handler = AsyncSlackRequestHandler(slack_app)
slack_commands = SlackAppCommands(app=slack_app)
