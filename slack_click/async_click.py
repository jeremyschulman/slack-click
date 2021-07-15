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

from typing import Coroutine, Callable, Any
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

__all__ = [
    "version_option",
    "click_async",
    "AsyncSlackClickGroup",
    "AsyncSlackClickCommand",
]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def click_async(callback=None):
    def wrapped(func):
        @wraps(func)
        def new_callback(*vargs, **kwargs):
            ctx = g_click_context.get()
            if ctx.invoked_subcommand:
                return

            # presume the orig_callback was defined as an async def.  Therefore
            # defer the execution of the coroutine to the calling main.
            return func(*vargs, **kwargs)

        return new_callback

    return wrapped if not callback else wrapped(callback)


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

    async def send_version(ctx: click.Context, message: str):
        slack_cmd: SlackClickHelper = ctx.command
        request = slack_cmd.obj_slack_request(ctx.obj)
        await request.context["say"](f"```{message}```")

    def decorator(func):
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
        return decorators.option(*(param_decls or ("--version",)), **attrs)(func)

    return decorator


class SlackClickHelper(Command):
    def __init__(self, *vargs, **kwargs):
        self.event_id = kwargs.get("name")
        self.obj_slack_request: Callable[[Any], Request] = kwargs.pop(
            "slack_request", self._slack_request_is_obj
        )
        super(SlackClickHelper, self).__init__(*vargs, **kwargs)

    @staticmethod
    def _slack_request_is_obj(obj):
        return obj

    @staticmethod
    def slack_format_usage_help(command: dict, ctx: click.Context, errmsg: str):
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
    def slack_format_help(ctx: click.Context):
        help_text = ctx.get_help()
        return dict(text=f"*Command help:*\n```{help_text}```", fallback=help_text)

    def get_help_option(self, ctx):
        help_options = self.get_help_option_names(ctx)
        if not help_options or not self.add_help_option:
            return

        def slack_show_help(_ctx: click.Context, param, value):  # noqa
            if value and not _ctx.resilient_parsing:
                payload = self.slack_format_help(_ctx)
                slack_cmd: SlackClickHelper = _ctx.command
                request = slack_cmd.obj_slack_request(ctx.obj)
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

    def make_context(self, info_name, args, parent=None, **extra):
        ctx = super(SlackClickHelper, self).make_context(
            info_name=info_name, args=args, parent=parent, **extra
        )
        g_click_context.set(ctx)
        return ctx

    async def __call__(self, *vargs, **kwargs):
        await self.main(*vargs, **kwargs)

    async def main(
        self,
        args=None,
        prog_name=None,
        complete_var=None,
        standalone_mode=False,
        **extra,
    ):

        if (obj := extra.get("obj")) is None:
            raise ValueError("Missing obj to contain Slack-Bolt request, required.")

        request = self.obj_slack_request(obj)

        if not isinstance(request, Request):
            raise ValueError(
                "obj missing expected Slack-Bolt request instance, required."
            )

        # if args are not explicitly provided, then examine the slack command
        # request 'text' field in the payload body.

        if not args:
            args = request.body.get("text", "").split()

        try:
            # Call the Click main method for this Command/Group instance.  The
            # result will either be that a handler returned a coroutine for
            # async handling, or there is an Exception that needs to be
            # handled.

            cli_coro = super(SlackClickHelper, self).main(
                args, prog_name, complete_var, standalone_mode, **extra
            )

            if isinstance(cli_coro, Coroutine):
                return await cli_coro

        except click.exceptions.UsageError as exc:
            ctx = (
                exc.ctx
                or g_click_context.get()
                or self.make_context(self.name, args, obj=obj)
            )

            payload = self.slack_format_usage_help(
                request.body, ctx, errmsg=exc.format_message()
            )

            await request.context["say"](**payload)
            return

        except click.exceptions.Exit:
            return


class AsyncSlackClickCommand(SlackClickHelper, Command):
    pass


class AsyncSlackClickGroup(SlackClickHelper, Group):
    def __init__(self, *vargs, **kwargs):
        self.ic = pyee.EventEmitter()
        kwargs.setdefault("invoke_without_command", True)
        super(AsyncSlackClickGroup, self).__init__(*vargs, **kwargs)

    @staticmethod
    def as_async_group(func):
        orig_callback = func.callback

        @wraps(func)
        def new_callback(*vargs, **kwargs):
            ctx = _contextvar_get_current_context()
            if ctx.invoked_subcommand:
                return

            # presume the orig_callback was defined as an async def.  Therefore
            # defer the execution of the coroutine to the calling main.
            return orig_callback(*vargs, **kwargs)

        func.callback = new_callback
        return func

    def add_command(self, cmd, name=None):
        # need to wrap Groups in async handler since the underlying Click code
        # is assuming sync processing.
        cmd.event_id = f"{self.event_id}.{name or cmd.name}"

        if isinstance(cmd, AsyncSlackClickGroup):
            cmd = self.as_async_group(cmd)

        super(AsyncSlackClickGroup, self).add_command(cmd, name)

    def command(self, *args, **kwargs):
        kwargs.setdefault("cls", AsyncSlackClickCommand)
        return super().command(*args, **kwargs)

    def group(self, *args, **kwargs):
        kwargs.setdefault("cls", AsyncSlackClickGroup)
        return super().group(*args, **kwargs)

    # -------------------------------------------------------------------------
    # Used for interactive workflows such as button-press so that the
    # associated click groups/command is invoked.
    # -------------------------------------------------------------------------

    def on(self, cmd: AsyncSlackClickCommand):
        def wrapper(func):
            self.ic.on(cmd.event_id, func)

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


g_click_context = ContextVar("click_context")


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
        return g_click_context.get()
    except LookupError:
        if not silent:
            raise RuntimeError("There is no active click context.")


click.decorators.get_current_context = _contextvar_get_current_context
