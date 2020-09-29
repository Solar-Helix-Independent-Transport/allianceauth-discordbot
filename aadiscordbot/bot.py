import logging
import sys
import traceback
import os

import aiohttp
import aioredis
import pendulum
import json
from celery import shared_task
from .cogs.utils import context

import discord
from discord.ext import commands, tasks

import django
from django.conf import settings
import django.db


description = """
AuthBot is watching...
"""

logger = logging.getLogger(__name__)

initial_cogs = (
    "cogs.about",
    "cogs.members",
    "cogs.timers",
    "cogs.auth",
    "cogs.sov",
    "cogs.zkill",
    "cogs.time"
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
        activity = discord.Activity(name="Everything!",
                                    application_id=0,
                                    type=discord.ActivityType.watching,
                                    state="Monitoring",
                                    details="Waiting for Shenanigans!",
                                    emoji={"name":":smiling_imp:"}
                                    )
        await self.change_presence(activity=activity)
        await self.queue_consumer.start()
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
        if (message.channel.id not in settings.ADMIN_DISCORD_BOT_CHANNELS) and (message.channel.id not in settings.ADM_DISCORD_BOT_CHANNELS) and (message.channel.id not in settings.SOV_DISCORD_BOT_CHANNELS):
            return
        await self.process_commands(message)

    @tasks.loop(seconds=30.0)
    async def queue_consumer(self):
        logger.error("Queue Consumer has Looped")
        try:
            task = await get_task()
            logger.error(task)
            logger.error(task["body"])
            logger.error(task["headers"])
            task_headers = task["headers"]
            logger.error(task_headers["task"])
            logger.error(task_headers["argsrepr"])
            task_header_args = task_headers["argsrepr"].strip(']()[').split(', ') 
            logger.error(task_header_args[0])
            logger.error(task_header_args[1])
            logger.error("i have debugd")

            if task_headers["task"] == 'aadiscordbot.tasks.send_channel_message':
                logger.error("I am running a Send Channel Message Task")
                channel_id = int(task_header_args[0])
                await self.get_channel(channel_id).send(task_header_args[1])

            elif task_headers["task"] == 'aadiscordbot.tasks.send_direct_message':
                logger.error("i am running a Direct Message Task")
                user_id = int(task_header_args[0])

                if await self.get_user(user_id).dm_channel != None:
                    await self.get_user(user_id).dm_channel.send(task_header_args[1])
                else:
                    await self.get_user(user_id).create_dm()
                    await self.get_user(user_id).dm_channel.send(task_header_args[1])

            else:
                logged.error("i did nothing")

        except Exception as e:
            logger.error(e)
        

    async def on_resumed(self):
        print("Resumed...")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            print(error)
            await ctx.send(error)
        elif isinstance(error, commands.MissingRequiredArgument):
            print(error)
            await ctx.send(error)
        elif isinstance(error, commands.NoPrivateMessage):
            print(error)
            await ctx.send(error)
        elif isinstance(error, commands.CommandInvokeError):
            print(error)
            return await ctx.send(error)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                "Sorry, I don't have the required permissions to do that here:\n{0}".format(error.missing_perms)
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Sorry, you do not have permission to do that here.")
        elif isinstance(error, commands.NotOwner):
            print(error)
            await ctx.send(error)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.message.add_reaction(chr(0x274C))

    def run(self):
        super().run(settings.DISCORD_BOT_TOKEN, reconnect=True)

## Fetching Tasks from celery queue for the message sending loop
async def get_task(queuename="aadiscordbot"):
    logger.error("im getting a task")
    try:
        r = await aioredis.create_redis(settings.BROKER_URL)
        task = await r.lpop(queuename)
        logger.error('ive got a task')
        logger.error(task)
        task_decoded = task.decode()
        return json.loads(task_decoded)
    except Exception as e:
        logger.error(e)
        pass