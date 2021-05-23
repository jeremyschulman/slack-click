from fastapi import FastAPI
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_click.app_click import SlackAppCommands

slack_app = AsyncApp()
slack_app_handler = AsyncSlackRequestHandler(slack_app)
api = FastAPI()
slack_commands = SlackAppCommands(app=slack_app)
