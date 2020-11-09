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
from . import bot_tasks

import discord
from discord.ext import commands, tasks

import django
from django.conf import settings
import django.db

import celery

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
    "cogs.time",
)
queuename="aadiscordbot"
queue_keys = [f"{queuename}", 
              f"{queuename}\x06\x161", 
              f"{queuename}\x06\x162", 
              f"{queuename}\x06\x163", 
              f"{queuename}\x06\x164", 
              f"{queuename}\x06\x165", 
              f"{queuename}\x06\x166", 
              f"{queuename}\x06\x167", 
              f"{queuename}\x06\x168", 
              f"{queuename}\x06\x169"]

class AuthBot(commands.Bot):
    def __init__(self):
        client_id = settings.DISCORD_APP_ID

        intents = discord.Intents.default()
        intents.members = True

        super().__init__(
            command_prefix="!",
            description=description,
            intents=intents,
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
        self.queue_runner.start()
        logger.info("Ready")

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

    @tasks.loop(seconds=30.0)
    async def queue_runner(self):
        logger.debug("Queue Runner started")
        tasks = []
        task = True
        while task != False:
            task = await get_task(self)
            if task:
                await self.queue_consumer(task)

        logger.debug(f"Queue Runner ran {len(tasks)} tasks")

        # do we want to process results?

    async def queue_consumer(self, task):
        logger.debug("Queue Consumer has started")
        try:
            task_headers = task["headers"]
            task_header_args = eval(task_headers["argsrepr"])

            if 'aadiscordbot.tasks.' in task_headers["task"]:
                task = task_headers["task"].replace("aadiscordbot.tasks.", '')
                task_function = getattr(bot_tasks, task, False)
                if task_function:
                    await task_function(self, task_header_args)
                else:
                    logger.debug("No bot_task for that auth_task?")
            else:
                logger.debug("i got an invalid auth_task")

        except Exception as e:
            logger.error("Queue Consumer Failed")
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
async def get_task(bot):
    logger.debug("im getting a task")
    try:
        task = await bot.redis.execute("brpop", queuename, *queue_keys, 1)
        if task != None:
            logger.info('ive got a task')
            logger.debug(task)
            return json.loads(task[1])
        else:
            logger.debug("No tasks in queue")
            return False

    except Exception as e:
        logger.error("Get Task Failed")
        logger.error(e)
        pass