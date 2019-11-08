import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "isfauth.settings.local")

from aadiscordbot import launcher
import click
import asyncio
@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        loop = asyncio.get_event_loop()
        launcher.run_bot()

if __name__ == "__main__":
    main()
