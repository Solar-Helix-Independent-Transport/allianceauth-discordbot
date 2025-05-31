import logging
import time
import traceback
from datetime import datetime
from socket import timeout

import aiohttp
import discord
import pendulum
from celery.utils.time import rate
from discord import ApplicationContext, DiscordException
from discord.ext import commands, tasks
from kombu import Connection, Consumer, Queue
from kombu.utils.limits import TokenBucket
from redis import asyncio as aioredis

import django
import django.db
from django.conf import settings
from django.utils import timezone

from allianceauth import hooks

import aadiscordbot
from aadiscordbot import app_settings
from aadiscordbot.app_settings import (
    DISCORD_BOT_ACCESS_DENIED_REACT, DISCORD_BOT_PREFIX,
)
from aadiscordbot.cogs.utils.exceptions import NotAuthenticated, NotManaged

from . import bot_tasks

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
        limit = rate(
            app_settings.DISCORD_BOT_TASK_RATE_LIMITS.get(task, "100/s"))
        return TokenBucket(limit, capacity=1)

    def check_rate_limit(self, task):
        if task not in self.rate_buckets:
            self.rate_buckets[task] = self.bucket_for_task(task)
        # logger.debug(f" {self.rate_buckets[task].capacity} {self.rate_buckets[task].fill_rate} {self.rate_buckets[task].expected_time()}")
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
        self.client_id = client_id
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = app_settings.DISCORD_BOT_MESSAGE_INTENT

        super().__init__(
            command_prefix=DISCORD_BOT_PREFIX,
            description=description,
            intents=intents,
        )
        print(f"Authbot Started with command prefix {DISCORD_BOT_PREFIX}")

        # Set some base stuff up
        self.tasks = []
        self.pending_tasks = PendingQueue()
        self.rate_limits = RateLimiter()
        self.statistics = Statistics()
        self.cog_names_loaded = []
        self.cog_names_failed = []

        # Load our hooks
        hooks_ = hooks.get_hooks("discord_cogs_hook")
        for hook in hooks_:
            for cog in hook():
                try:
                    self.load_extension(cog)
                    self.cog_names_loaded.append(cog)
                except Exception:
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
        logger.info("Starting on_ready")

        logger.info("Setting bot activity")
        activity = discord.Activity(name="Everything!",
                                    application_id=0,
                                    type=discord.ActivityType.watching,
                                    state="Monitoring",
                                    details="Waiting for Shenanigans!",
                                    emoji={"name": ":smiling_imp:"}
                                    )
        await self.change_presence(activity=activity)
        logger.info("Bot activity set")

        logger.info("Creating aiohttp session")
        self.session = aiohttp.ClientSession()
        logger.info(f"aiohttp session started {self.session}")

        logger.info("Creating redis pool")
        self.redis = None
        self.redis = aioredis.from_url(
            getattr(
                settings,
                "BROKER_URL",
                "redis://localhost:6379/0"
            ),
            encoding="utf-8",
            decode_responses=True
        )

        logger.info(f"redis pool started {self.redis}")

        if not hasattr(self, "currentuptime"):
            self.currentuptime = pendulum.now(tz="UTC")

        if not hasattr(self, "statistics"):
            self.statistics.start_time = timezone.now()

        logger.info("Starting task connection")
        self.message_connection = Connection(
            getattr(
                settings,
                "BROKER_URL",
                'redis://localhost:6379/0'
            )
        )
        logger.info(f"Task connection created {self.message_connection}")

        queues = []
        for que in queue_keys:
            queues.append(Queue(que))

        logger.info("Creating task consumer")
        self.message_consumer = Consumer(
            self.message_connection,
            queues,
            callbacks=[
                self.on_queue_message
            ],
            accept=['json']
        )
        logger.info(f"Task consumer created {self.message_consumer}")
        logger.info("Starting task loop")
        self.poll_queue.start()
        logger.info("on_ready Complete!")

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
        except Exception as e:
            logger.error(f"Interaction Failed {e}", stack_info=True)
        django.db.close_old_connections()

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def sync_commands(self, *args, **kwargs):
        try:
            return await super(__class__, self).sync_commands(*args, **kwargs)
        except discord.Forbidden as e:
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
            logger.error(e)

    @tasks.loop(seconds=1.0)
    async def poll_queue(self):
        message_avail = True
        while message_avail:
            try:
                with self.message_consumer:
                    self.message_connection.drain_events(timeout=0.01)
            except timeout:
                # This is when there are no messages in the queue.
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
            logger.error(error)
            await ctx.send(error)
        elif isinstance(error, commands.MissingRequiredArgument):
            logger.error(error)
            await ctx.send(error)
        elif isinstance(error, commands.NoPrivateMessage):
            logger.error(error)
            await ctx.send(error)
        elif isinstance(error, commands.CommandInvokeError):
            logger.error(error)
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
            logger.error(error)
            await ctx.send(error)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.message.add_reaction(chr(0x274C))
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(error)
        else:
            logger.error(f"Unknown Error {error}", exc_info=True)
            await ctx.send("Something Went Wrong, Please try again Later.",)
        django.db.close_old_connections()

    async def send_resp(self, ctx, exp):
        try:
            await ctx.send_response(exp, ephemeral=True)
        except RuntimeError:
            await ctx.send_followup(exp, ephemeral=True)

    async def on_application_command_error(self, context: ApplicationContext, exception: DiscordException) -> None:
        if isinstance(exception, commands.CheckFailure):
            await self.send_resp(context, exception)
        elif isinstance(exception, commands.MissingPermissions):
            await self.send_resp(context, exception)
        elif isinstance(exception, NotAuthenticated):
            await self.send_resp(context, exception)
        elif isinstance(exception, NotManaged):
            await self.send_resp(context, exception)
        else:  # Catch everything, and close out the interactions gracefully.
            logger.error(f"Unknown Error {exception}")
            logger.error("\n".join(traceback.format_tb(
                exception.original.__traceback__)))

            if app_settings.DISCORD_BOT_SEND_FAILURE_MESSAGES and app_settings.DISCORD_BOT_FAILURE_MESSAGES_CHANNEL:
                message = [f"`{context.command}` failed for `{context.author}`\n",
                           f"**Exception:** ```{exception}```",
                           f"\n**Interaction:** ```{str(context.interaction.data).replace('`', ' `')}```",
                           "\n**Trace:**```"]
                message += traceback.format_tb(
                    exception.original.__traceback__)
                message.append("\n```")
                from . import tasks
                tasks.send_message(message="\n".join(message),
                                   channel_id=app_settings.DISCORD_BOT_FAILURE_MESSAGES_CHANNEL)
            await context.respond("Something Went Wrong, Please try again Later.", ephemeral=True)
        django.db.close_old_connections()

    def run(self):
        try:
            logger.info(
                "******************************************************"
            )
            logger.info(
                "         ##            Alliance Auth 'AuthBot'"
            )
            logger.info(
                f"        ####           Version         :  {aadiscordbot.__version__}"
            )
            logger.info(
                f"       #######         Branch          :  {aadiscordbot.__branch__}"
            )
            logger.info(
                f"      #########        Message Intents :  {app_settings.DISCORD_BOT_MESSAGE_INTENT}"
            )
            logger.info(
                f"     ######## ((       Prefix          :  {app_settings.DISCORD_BOT_PREFIX}"
            )
            logger.info(
                f"    ###### ((((((      Bot Join Link   :  {INVITE_URL}"
            )
            logger.info(
                "   ###        ((((     Starting up..."
            )
            logger.info(
                "  ##             (("
            )
            logger.info(
                "                       [Cogs Loaded]"
            )
            for c in self.cog_names_loaded:
                logger.info(
                    f"                         - {c}"
                )
            if len(self.cog_names_failed):
                logger.info(
                    "                       [Cog Failures]"
                )
                for c in self.cog_names_failed:
                    logger.info(f"                         - {c}")
            logger.info(
                "******************************************************"
            )
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
