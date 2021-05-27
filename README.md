# Click support for Slack Apps

As a Python
[Slack-Bolt](https://slack.dev/bolt-python/tutorial/getting-started)
application developer I want to create slash-command that are composed with the
Python [Click](https://click.palletsprojects.com/) package.  I use the
[FastAPI](https://fastapi.tiangolo.com/) web framework in asyncio mode.

I need support for  `--help` `--version` and any usage error to be properly
sent as Slack messages.

# Quick Start

Check out the [example](example/README.md) application.

# Usage

The `slack-click` packagage provides the following to support the Slack environment:

* *SlackClickCommand* - used as the `cls` parameter to the click.command decorator
* *SlackClickGroup* - used as the `cls` parameter to the click.group decorator
* *version_option* - used in the same was as the standard click.version_option decorator

The `slack-click` package provides a Slack Bolt registry adapter `SlackAppCommands`.

Example for integrating with a Slack Bolt application:

```python
from fastapi import FastAPI
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_click import SlackAppCommands

api = FastAPI()
slack_app = AsyncApp()
slack_socket_handler = AsyncSocketModeHandler(slack_app)
slack_commands = SlackAppCommands(app=slack_app)
```

The `slack_commands` instance provides a `.register()` method decorator that is
used to hook in the Slack bolt command handler process.  See examples below.

---
Example for definiting a Click command handler:

```python
import click
from slack_click import SlackClickCommand, version_option
from slack_bolt.request.async_request import AsyncBoltRequest as Request

@slack_commands.register()
@click.command(name="/ping", cls=SlackClickCommand)
@version_option(version="0.1.0")
@click.pass_obj
async def cli_ping_command(obj: dict):
    request: Request = obj["request"]
    say = request.context["say"]
    await say(f"Hiya <@{request.context.user_id}>.  Ping back at you :eyes:")
```

---

Example for definiting a Click group handler "click" with a command "hello".

```python
import click
from slack_bolt.request.async_request import AsyncBoltRequest as Request
from slack_click import SlackClickGroup, version_option

@slack_commands.register()
@click.group(name="/click", cls=SlackClickGroup)
@version_option(version="0.1.0")
@click.pass_obj
async def cli_click_group(obj: dict):
    """
    This is the Clicker /click command group
    """
    request: Request = obj["request"]
    say = request.context["say"]
    await say("`/click` command invoked without any commands or options.")


@cli_click_group.command("hello")
@click.pass_obj
async def click_hello_command(obj):
    request: Request = obj["request"]
    await request.context.say(f"Hi there <@{request.context.user_id}> :eyes:")
```

# Customizing Help

# References
* [Click Package Home](https://click.palletsprojects.com/)
* [Getting Started with Slack Bolt](https://slack.dev/bolt-python/tutorial/getting-started)
* [Slack-Bolt-Python Github](https://github.com/slackapi/bolt-python)
* [Internals of Bolt Callback Parameters](https://github.com/slackapi/bolt-python/blob/main/slack_bolt/listener/async_internals.py)
