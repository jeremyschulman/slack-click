from click import get_current_context

from slack_bolt.context.ack.async_ack import AsyncAck as Ack
from slack_bolt.request.async_request import AsyncBoltRequest as Request


class SlackAppCommands(object):
    def __init__(self, app):
        self.app = app
        self._registry = dict()

    def register(self, f=None):
        def wrapped(f):
            orig_callback = f.callback

            def new_callback(*vargs, **kwargs):
                ctx = get_current_context()
                if ctx.invoked_subcommand:
                    return

                # presume the orig_callback was defined as an async def.  Therefore
                # defer the execution of the coroutine to the calling main.
                return orig_callback(*vargs, **kwargs)

            f.callback = new_callback
            self._registry[f.name] = f  # noqa
            f.event_name = f.name

            @self.app.command(f.name)
            async def on_click(ack: Ack, request: Request, command: dict):
                await ack()
                await f.run(request=request, command=command)

            return f

        return wrapped if not f else wrapped(f)
