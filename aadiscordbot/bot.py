import logging
import sys
import traceback
import os
import aiohttp
import aioredis
import pendulum

from discord.ext import commands
import django

import discord
from .cogs.utils import context
from django.conf import settings
import django.db

description = """
AuthBot is watching...
"""

log = logging.getLogger(__name__)

initial_cogs = (
    "cogs.about",
    "cogs.members",
    "cogs.timers",
)

class AuthBot(commands.Bot):
    def __init__(self):
        client_id = settings.DISCORD_APP_ID


        super().__init__(
            command_prefix="!",
            description=description,
        )
        self.redis = None
        self.redis = self.loop.run_until_complete(aioredis.create_pool(("localhost", 6379), minsize=5, maxsize=10))
        print('redis pool started', self.redis)
        self.client_id = client_id
        self.session = aiohttp.ClientSession(loop=self.loop)
        django.setup()        
        for cog in initial_cogs:
            try:
                self.load_extension("aadiscordbot.{0}".format(cog))
            except Exception as e:
                print(f"Failed to load cog {cog}", file=sys.stderr)
                traceback.print_exc()

    async def on_ready(self):
        if not hasattr(self, "currentuptime"):
            self.currentuptime = pendulum.now(tz="UTC")
        await self.change_presence(activity=discord.Game(name="Alliance Manager"))
        print("Ready")

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=context.Context)

        if ctx.command is None:
            return
        django.db.close_old_connections()
        await self.invoke(ctx)
        django.db.close_old_connections()

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_resumed(self):
        print("Resumed...")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(error)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(error)
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(error)
        elif isinstance(error, commands.CommandInvokeError):
            return await ctx.send(error)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                "Sorry, I don't have the required permissions to do that here:\n{0}".format(error.missing_perms)
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Sorry, you do not have permission to do that here.")
        elif isinstance(error, commands.NotOwner):
            await ctx.send(error)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.message.add_reaction(chr(0x274C))

    def run(self):
        super().run(settings.DISCORD_BOT_TOKEN, reconnect=True)
