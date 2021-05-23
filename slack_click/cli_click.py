#  Copyright 2021 Jeremy Schulman, nwkautomaniac@gmail.com
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Coroutine
import asyncio
from functools import wraps
from contextvars import ContextVar

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click
from click import decorators
from click import Command, Option, Group
import pyee
from slack_bolt.request.async_request import AsyncBoltRequest as Request
from first import first

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["version_option", "SlackClickGroup", "SlackClickCommand", "SlackClickHelper"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def version_option(version: str, *param_decls, **attrs):
    """
    The Click version_option decorator used to support asyncio Slack
    applications.

    Parameters
    ----------
    version:
        The version string; required.

    param_decls:
        The list of parameter declarations as they are documented in
        Click.version_option.  These are optional; and adds "--version" just as
        it would with the Click package.

    attrs
        The keyword arguments supported by Click.version_option; used in the
        same manner as Click.

    Returns
    -------
    The decorator to be used as one would normally use @click.version_option(...)

    """

    async def send_version(ctx, message):
        request: Request = ctx.obj["request"]
        await request.context["say"](f"```{message}```")

    def decorator(f):
        prog_name = attrs.pop("prog_name", None)
        message = attrs.pop("message", "%(prog)s, version %(version)s")

        def callback(ctx, param, value):  # noqa
            if not value or ctx.resilient_parsing:
                return
            prog = prog_name
            if prog is None:
                prog = ctx.find_root().info_name

            asyncio.create_task(
                send_version(ctx, (message % {"prog": prog, "version": version}))
            )
            ctx.exit()

        attrs.setdefault("is_flag", True)
        attrs.setdefault("expose_value", False)
        attrs.setdefault("is_eager", True)
        attrs.setdefault("help", "Show the version and exit.")
        attrs["callback"] = callback
        return decorators.option(*(param_decls or ("--version",)), **attrs)(f)

    return decorator


class SlackClickHelper(Command):
    def __init__(self, *vargs, **kwargs):
        self.event_id = kwargs.get("name")
        super(SlackClickHelper, self).__init__(*vargs, **kwargs)

    @staticmethod
    def format_slack_usage_help(command: dict, ctx: click.Context, errmsg: str):
        """
        This function returns a dictionary formatted with the Slack message
        that will be sent to the User upon any command usage error.  As a
        Developer you may want to change the response content/format for this
        type of help.

        Parameters
        ----------
        command: dict
            The command data from the Slack request

        ctx: click.Context
            The Click context processing the User command.

        errmsg: str
            The speific usage error message, generally produced by the Click package depending
            on the offending User input.

        Returns
        -------
        dict
            The Slack message body dictionary that will be returned to the Slack User.
        """
        help_text = ctx.get_help()
        msg_body = dict()
        atts = msg_body["attachments"] = list()

        try_cmd = f"{command['command']} {command['text']}"
        user_id = command["user_id"]

        atts.append(
            dict(
                color="#FF0000",  # red
                pretext=f"Hi <@{user_id}>, I could not run your command",
                text=f"```{try_cmd}```",
                fallback=try_cmd,
            )
        )

        atts.append(dict(text=f"```{errmsg}```", fallback=errmsg))

        atts.append(
            dict(pretext="Command help", text=f"```{help_text}```", fallback=help_text)
        )
        return msg_body

    @staticmethod
    def format_slack_help(ctx: click.Context):
        help_text = ctx.get_help()
        return dict(text=f"*Command help:*\n```{help_text}```", fallback=help_text)

    def get_help_option(self, ctx):
        help_options = self.get_help_option_names(ctx)
        if not help_options or not self.add_help_option:
            return

        def slack_show_help(_ctx: click.Context, param, value):  # noqa
            if value and not _ctx.resilient_parsing:
                payload = self.format_slack_help(_ctx)
                request: Request = _ctx.obj["request"]
                asyncio.create_task(request.context["say"](**payload))
                _ctx.exit()

        return Option(
            help_options,
            is_flag=True,
            is_eager=True,
            expose_value=False,
            callback=slack_show_help,
            help="Show this message and exit.",
        )

    def invoke(self, ctx):
        """
        return the coroutine ready for await, but cannot await here ...
        execution deferred to the `run` method that is async.
        """
        click_context.set(ctx)
        return super().invoke(ctx)

    async def run(self, request: Request, command: dict):
        args = command.get("text", "").split()
        ctx_obj = dict(request=request, command=command)

        try:
            # Call the Click main method for this Command/Group instance.  The
            # result will either be that a handler returned a coroutine for
            # async handling, or there is an Exception that needs to be
            # handled.

            cli_coro = self.main(
                args=args, prog_name=self.name, obj=ctx_obj, standalone_mode=False
            )

            if isinstance(cli_coro, Coroutine):
                return await cli_coro

        except click.exceptions.UsageError as exc:
            ctx = (
                exc.ctx
                or click_context.get()
                or self.make_context(self.name, args, obj=ctx_obj)
            )
            payload = self.format_slack_usage_help(
                command, ctx, errmsg=exc.format_message()
            )
            await request.context["say"](**payload)
            return

        except click.exceptions.Exit:
            return


class SlackClickCommand(SlackClickHelper, Command):
    pass


class SlackClickGroup(SlackClickHelper, Group):
    def __init__(self, *vargs, **kwargs):
        self.ic = pyee.EventEmitter()
        kwargs["invoke_without_command"] = True
        super(SlackClickGroup, self).__init__(*vargs, **kwargs)

    @staticmethod
    def as_async_group(f):
        orig_callback = f.callback

        @wraps(f)
        def new_callback(*vargs, **kwargs):
            ctx = _contextvar_get_current_context()
            if ctx.invoked_subcommand:
                return

            # presume the orig_callback was defined as an async def.  Therefore
            # defer the execution of the coroutine to the calling main.
            return orig_callback(*vargs, **kwargs)

        f.callback = new_callback
        return f

    def add_command(self, cmd, name=None):
        # need to wrap Groups in async handler since the underlying Click code
        # is assuming sync processing.
        cmd.event_id = f"{self.event_id}.{name or cmd.name}"

        if isinstance(cmd, SlackClickGroup):
            cmd = self.as_async_group(cmd)

        super(SlackClickGroup, self).add_command(cmd, name)

    def command(self, *args, **kwargs):
        kwargs["cls"] = SlackClickCommand
        return super().command(*args, **kwargs)

    def group(self, *args, **kwargs):
        kwargs["cls"] = SlackClickGroup
        return super().group(*args, **kwargs)

    def on(self, cmd: SlackClickCommand):
        def wrapper(f):
            self.ic.on(cmd.event_id, f)

        return wrapper

    async def emit(self, request: Request, event: str):
        handler = first(self.ic.listeners(event))

        if handler is None:
            log = request.context.logger
            log.critical(f"No handler for command option '{event}'")
            return

        return await handler(request)


# -----------------------------------------------------------------------------
#    WARNING! WARNING! WARNING! WARNING! WARNING! WARNING! WARNING! WARNING!
# -----------------------------------------------------------------------------
#                   Monkey-Patching Click for Asyncio Support
# -----------------------------------------------------------------------------

# the click context "context var" is used to support asyncio environments; and
# the following private function _contextvar_get_current_context is
# monkeypatched into the Click package do avoid the use of the threading.local
# stack (as implemented in Click).


click_context = ContextVar("click_context")


def _contextvar_get_current_context(silent=False):
    """Returns the current click context.  This can be used as a way to
    access the current context object from anywhere.  This is a more implicit
    alternative to the :func:`pass_context` decorator.  This function is
    primarily useful for helpers such as :func:`echo` which might be
    interested in changing its behavior based on the current context.

    To push the current context, :meth:`Context.scope` can be used.

    .. versionadded:: 5.0

    :param silent: if set to `True` the return value is `None` if no context
                   is available.  The default behavior is to raise a
                   :exc:`RuntimeError`.
    """
    try:
        return click_context.get()
    except LookupError:
        if not silent:
            raise RuntimeError("There is no active click context.")


click.decorators.get_current_context = _contextvar_get_current_context
