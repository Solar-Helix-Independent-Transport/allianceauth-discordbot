import logging
import sys
import time
import traceback
from datetime import datetime
from socket import timeout
from typing import Dict
from aadiscordbot.cogs.utils.exceptions import NotAuthenticated

import aiohttp
import aioredis
import discord
import pendulum
from celery.utils.time import rate
from discord import ApplicationContext, DiscordException
from discord.ext import commands, tasks
from kombu import Connection, Consumer, Queue
from kombu.utils.limits import TokenBucket

import django
import django.db
from django.conf import settings
from django.utils import timezone

from allianceauth import hooks

import aadiscordbot
from aadiscordbot import app_settings
from aadiscordbot.app_settings import (
    DISCORD_BOT_ACCESS_DENIED_REACT, DISCORD_BOT_MESSAGE_INTENT,
    DISCORD_BOT_PREFIX,
)

from . import bot_tasks
from .cogs.utils import context

description = """
AuthBot is watching...
"""

logger = logging.getLogger(__name__)

INVITE_URL = f"https://discord.com/api/oauth2/authorize?client_id={app_settings.DISCORD_APP_ID}&permissions=8&scope=bot%20applications.commands"

queuename = "aadiscordbot"
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


class PendingQueue:
    def __init__(self):
        self.data = []

    def append(self, data):
        self.data.append(data)
        self.data.sort(key=lambda a: a[0])

    def pop_next(self):
        next_task = next(
            (x for x in self.data if x[0] < timezone.now()), False)
        if next_task:
            del (self.data[self.data.index(next_task)])
        return next_task

    def outstanding(self):
        return len(self.data)


class RateLimiter:
    def __init__(self):
        self.rate_buckets = {}

    def bucket_for_task(self, task):
        limit = rate(app_settings.DISCORD_BOT_TASK_RATE_LIMITS.get(task, None))
        return TokenBucket(limit, capacity=1) if limit else None

    def check_rate_limit(self, task):
        if task not in self.rate_buckets:
            self.rate_buckets[task] = self.bucket_for_task(task)
        #logger.debug(f" {self.rate_buckets[task].capacity} {self.rate_buckets[task].fill_rate} {self.rate_buckets[task].expected_time()}")
        return self.rate_buckets[task].can_consume()

    def to_string(self):
        """
            Print of Task Limiter Stats
        """
        out = ["```"]
        for t, d in self.rate_buckets.items():
            out.append(
                f"{t}\n   Rate:  {d.fill_rate:.2}\n   TTL:   {d.expected_time():.2}")
        out.append("```")
        return "\n".join(out)


class Statistics:
    def __init__(self):
        self.task_buckets = {}
        self.start_time = timezone.now()

    def add_task(self, task):
        date = timezone.now().strftime("%Y/%m/%d")
        if date not in self.task_buckets:
            self.task_buckets[date] = {}
        if task not in self.task_buckets[date]:
            self.task_buckets[date][task] = 0
        self.task_buckets[date][task] += 1

    def reset(self):
        self.task_buckets = {}

    def to_string(self):
        """
            Print of Run Task Stats
        """
        gap = "                                         "
        hdr = "  Task                                   Count"
        out = ["```", "Date"]
        for d, ts in self.task_buckets.items():
            out.append(f"{d}")
            out.append(hdr)
            for t, c in ts.items():
                out.append(f"    {t}{gap[len(str(t)):41]}{c}")
            out.append("\n")
        out.append("```")
        return "\n".join(out)


class AuthBot(commands.Bot):
    def __init__(self):
        django.setup()
        client_id = app_settings.DISCORD_APP_ID
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = app_settings.DISCORD_BOT_MESSAGE_INTENT

        super().__init__(
            command_prefix=DISCORD_BOT_PREFIX,
            description=description,
            intents=intents,
        )
        print(f"Authbot Started with command prefix {DISCORD_BOT_PREFIX}")

        self.redis = None
        self.redis = self.loop.run_until_complete(aioredis.create_pool(getattr(
            settings, "BROKER_URL", "redis://localhost:6379/0"), minsize=5, maxsize=10))
        print('redis pool started', self.redis)
        self.client_id = client_id
        self.session = aiohttp.ClientSession(loop=self.loop)

        self.tasks = []
        self.pending_tasks = PendingQueue()
        self.rate_limits = RateLimiter()
        self.statistics = Statistics()

        self.message_connection = Connection(
            getattr(settings, "BROKER_URL", 'redis://localhost:6379/0'))

        queues = []
        for que in queue_keys:
            queues.append(Queue(que))

        self.message_consumer = Consumer(self.message_connection, queues, callbacks=[
                                         self.on_queue_message], accept=['json'])

        self.cog_names_loaded = []
        self.cog_names_failed = []
        hooks_ = hooks.get_hooks("discord_cogs_hook")
        for hook in hooks_:
            for cog in hook():
                try:
                    self.load_extension(cog)
                    self.cog_names_loaded.append(cog)
                except Exception as e:
                    logger.exception(f"Failed to load cog {cog}")
                    self.cog_names_failed.append(cog)

    def on_queue_message(self, body, message):
        logger.debug(f'RECEIVED MESSAGE: {body!r}')
        try:
            task_headers = message.headers
            eta = task_headers.get("eta", False)
            _args = body[0]
            _kwargs = body[1]

            if 'aadiscordbot.tasks.' in task_headers["task"]:
                task = task_headers["task"].replace("aadiscordbot.tasks.", '')
                task_function = getattr(bot_tasks, task, False)
                if task_function:
                    if eta:
                        logger.debug(f"ETA RECEIVED: {eta}")
                        eta_date = datetime.fromisoformat(eta)
                        if eta_date < timezone.now():
                            self.tasks.append((task_function, _args, _kwargs))
                        else:
                            self.pending_tasks.append(
                                (eta_date, (task_function, _args, _kwargs)))
                    else:
                        self.tasks.append((task_function, _args, _kwargs))
                    if not bot_tasks.run_tasks.is_running():
                        bot_tasks.run_tasks.start(self)
                else:
                    logger.debug("No bot_task for that auth_task?")
            else:
                logger.debug("i got an invalid auth_task")

        except Exception as e:
            logger.error("Queue Consumer Failed")
            logger.error(e, exc_info=1)
        message.ack()

    async def on_ready(self):
        if not hasattr(self, "currentuptime"):
            self.currentuptime = pendulum.now(tz="UTC")
        if not hasattr(self, "statistics"):
            self.statistics.start_time = timezone.now()
        activity = discord.Activity(name="Everything!",
                                    application_id=0,
                                    type=discord.ActivityType.watching,
                                    state="Monitoring",
                                    details="Waiting for Shenanigans!",
                                    emoji={"name": ":smiling_imp:"}
                                    )
        await self.change_presence(activity=activity)

        self.poll_queue.start()
        logger.info("Ready")

    async def close(self):
        # return tasks to queue

        # recursive import
        from aadiscordbot import tasks as celery_tasks

        self.poll_queue.stop()
        bot_tasks.run_tasks.stop()

        recovered_messages = 0
        lost_messages = 0
        for task in self.tasks:
            task_function = getattr(celery_tasks, task[0].__name__, False)
            if task_function:
                recovered_messages += 1
                task_function.apply_async(args=task[1], kwargs=task[2])
            else:
                lost_messages += 1

        for task in self.pending_tasks.data:
            task_function = getattr(celery_tasks, task[1][0].__name__, False)
            if task_function:
                recovered_messages += 1
                task_function.apply_async(
                    args=task[1][1], kwargs=task[1][2], eta=task[0])
            else:
                lost_messages += 1

        if recovered_messages:
            logger.info(
                f"Returned {recovered_messages} message pending tasks to the celery queue")
        if lost_messages:
            logger.warning(
                f"Lost {recovered_messages} message pending tasks while trying to return them to the celery queue")

        await super().close()

    async def process_commands(self, message):
        ctx = await self.get_context(message)
        if ctx.command is None:
            return
        django.db.close_old_connections()
        await self.invoke(ctx)
        django.db.close_old_connections()

    async def on_interaction(self, interaction):
        try:
            django.db.close_old_connections()
            await self.process_application_commands(interaction)
            django.db.close_old_connections()
        except Exception as e:
            logger.error("Interaction Failed {e}", stack_info=True)

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def sync_commands(self, *args, **kwargs):
        try:
            return await super(__class__, self).sync_commands(*args, **kwargs)
        except discord.Forbidden:
            logger.error(
                "******************************************************")
            logger.error("|   AuthBot was Unable to Sync Slash Commands!!!!")
            logger.error(
                "|   Please ensure your bot was invited to the server with the correct scopes")
            logger.error("|")
            logger.error("|   To redo your scopes,")
            logger.error("|      1. Refresh Scopes with this link:")
            logger.error(f"|        {INVITE_URL}   ")
            logger.error(
                "|      2. Move the bots role to top of the roles tree if its not there already")
            logger.error("|      3. Restart Bot")
            logger.error(
                "******************************************************")

    @tasks.loop(seconds=1.0)
    async def poll_queue(self):
        message_avail = True
        while message_avail:
            try:
                with self.message_consumer:
                    self.message_connection.drain_events(timeout=0.01)
            except timeout as e:
                # logging.exception(e)
                message_avail = False

        next_task = self.pending_tasks.pop_next()
        while next_task:
            self.tasks.append(next_task[1])

            if not bot_tasks.run_tasks.is_running():
                bot_tasks.run_tasks.start(self)

            next_task = self.pending_tasks.pop_next()

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
                "Sorry, I don't have the required permissions to do that here:\n{}".format(
                    error.missing_permissions)
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.message.add_reaction(chr(DISCORD_BOT_ACCESS_DENIED_REACT))
            await ctx.message.reply("Sorry, you do not have permission to do that here.")
        elif isinstance(error, commands.NotOwner):
            print(error)
            await ctx.send(error)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.message.add_reaction(chr(0x274C))
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(error)

    async def on_application_command_error(self, context: ApplicationContext, exception: DiscordException) -> None: 
        if isinstance(exception, commands.CheckFailure):
            await context.send_response(exception, ephemeral = True)
        elif isinstance(exception, commands.MissingPermissions):
            await context.send_response(exception, ephemeral = True)
        elif isinstance(exception, NotAuthenticated):
            await context.send_response(exception, ephemeral = True)

    def run(self):
        # self.load_extension("aadiscordbot.slash.admin")
        try:

            logger.info(
                "******************************************************")
            logger.info(f"         ##            Alliance Auth 'AuthBot'")
            logger.info(
                f"        ####           Version         :  {aadiscordbot.__version__}")
            logger.info(
                f"       #######         Branch          :  {aadiscordbot.__branch__}")
            logger.info(
                f"      #########        Message Intents :  {app_settings.DISCORD_BOT_MESSAGE_INTENT}")
            logger.info(
                f"     ######## ((       Prefix          :  {app_settings.DISCORD_BOT_PREFIX}")
            logger.info(
                f"    ###### ((((((      Bot Join Link   :  {INVITE_URL}")
            logger.info(f"   ###        ((((     Starting up...")
            logger.info(f"  ##             ((")
            logger.info(f"                       [Cogs Loaded]")
            for c in self.cog_names_loaded:
                logger.info(f"                         - {c}")
            if len(self.cog_names_failed):
                logger.info(f"                       [Cog Failures]")
                for c in self.cog_names_failed:
                    logger.info(f"                         - {c}")
            logger.info(
                "******************************************************")
            super().run(app_settings.DISCORD_BOT_TOKEN, reconnect=True)
        except discord.PrivilegedIntentsRequired as e:
            logger.error("Unable to start bot with Messages Intent! Going to Sleep for 2min. "
                         "Please enable the Message Intent for your bot. "
                         "https://support-dev.discord.com/hc/en-us/articles/4404772028055"
                         f"{e}", exc_info=False)
            logger.info("If you wish to run without the Message Intent disable it in the local.py. "
                        "DISCORD_BOT_MESSAGE_INTENT=False", exc_info=False)
            time.sleep(120)
        except Exception as e:
            logger.error("Unable to start bot! going to sleep for 2 min. "
                         f"{e}", exc_info=True)
            time.sleep(120)
