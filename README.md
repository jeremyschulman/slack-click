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

# Async Usage

The following example illustrates how to device a Click group object and bind
it to the Slack-Bolt command listener.  In this example the code is all
asyncio.  Click was not written to support async io natively, so the
@click_async decorator is required.

By default the Developer should pass the Slack-Bolt request instance as the
Click obj value when executing the Click group/command.  There is a mechanism
to change this behavior, shown in a later example.

```python
import click
from slack_bolt.request.async_request import AsyncBoltRequest as Request
from slack_click.async_click import click_async, version_option, AsyncSlackClickGroup

# -----------------------------------------------------------------------------
# Define a Click group handler for the Slack Slash-Command
#
# Notes:
#   @click_async decorator must be used for asyncio mode
#   @click.pass_obj inserts the click.Context obj into the callback parameters
#       By default the obj is the Slack-Bolt request instance; see the
#       @app.command code further down.
# -----------------------------------------------------------------------------

@click.group(name="/clicker", cls=AsyncSlackClickGroup)
@version_option(version="0.1.0")
@click.pass_obj
@click_async
async def cli_click_group(request: Request):
    """
    This is the Clicker /click command group
    """
    say = request.context["say"]
    await say("`/click` command invoked without any commands or options.")


# -----------------------------------------------------------------------------
# Register the command with Slack-Bolt
# -----------------------------------------------------------------------------

@app.command(cli_click_group.name)
async def on_clicker(request: Request, ack, say):
    await ack()
    await say("Got it.")

    return await cli_click_group(prog_name=cli_click_group.name, obj=request)

# -----------------------------------------------------------------------------
# Add a command the Click group
# -----------------------------------------------------------------------------

@cli_click_group.command("hello")
@click.pass_obj
async def click_hello_command(request: Request):
    await request.context.say(f"Hi there <@{request.context.user_id}> :eyes:")
```

## Identifying the Slack-Bolt Request

As a Developer you may need to pass the Click obj as something other than the
bolt request direct, as shown in the example above.  You can identify
where the Slack-Bolt request object can be found in the obj by passing
a callback function to the click.command() or click.group() function called
`slack_request`.  This parameter expects a function that takes the click obj and
returns the slack request.

The example below uses an inline lambda to get the request from the obj as a
dictionary, using a the key "here".

```python
from random import randrange

import click
from slack_bolt.request.async_request import AsyncBoltRequest as Request
from slack_click.async_click import click_async, AsyncSlackClickCommand

# -----------------------------------------------------------------------------
# /fuzzy command to manifest an anminal
# -----------------------------------------------------------------------------


animals = [":smile_cat:", ":hear_no_evil:", ":unicorn_face:"]


@click.command(
    name="/fuzzy", cls=AsyncSlackClickCommand, slack_request=lambda obj: obj["here"]
)
@click_async
@click.pass_obj
async def cli_fuzzy_command(obj: dict):
    request = obj["here"]
    say = request.context["say"]
    this_animal = animals[randrange(len(animals))]

    await say(f"Poof :magic_wand: {this_animal}")


@app.command(cli_fuzzy_command.name)
async def on_fuzzy(request: Request, ack):
    await ack()
    return await cli_fuzzy_command(
        prog_name=cli_fuzzy_command.name, obj={"here": request}
    )
```

# Customizing Help

If you want to change the Slack message format for help or usage methods you can
subclass `AsyncSlackCLickCommand` or `AsyncSlackClickGroup` and overload the methods:

* *slack_format_help* - returns the Slack message payload (dict) for `--help`
* *slack_format_usage_help* - returns the Slack message payload (dict) when click exception `UsageError` is raised.


# References
* [Click - Docs Home](https://click.palletsprojects.com/)
* [Getting Started with Slack Bolt](https://slack.dev/bolt-python/tutorial/getting-started)
* [Slack-Bolt-Python Github](https://github.com/slackapi/bolt-python)
* [Internals of Bolt Callback Parameters](https://github.com/slackapi/bolt-python/blob/main/slack_bolt/listener/async_internals.py)
