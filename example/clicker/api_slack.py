from fastapi import Request

from .app_data import api, slack_app_handler


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
