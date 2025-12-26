import json
import logging

from aaprom.collectors.discordbot import bot_slash_command, bot_tasks_executed
from discord.errors import HTTPException
from discord.ext import commands

from ..app_settings import (
    DISCORD_BOT_FAILURE_MESSAGES_CHANNEL, DISCORD_BOT_SEND_FAILURE_MESSAGES,
)
from ..tasks import send_message

logger = logging.getLogger(__name__)


class PromExporter(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_application_command")
    async def internal_on_application_command(self, ctx):
        bot_slash_command.labels(command=str(ctx.command), user=str(
            ctx.author), guild=str(ctx.guild)).inc()

    @commands.Cog.listener("on_authbot_task_completed")
    async def on_authbot_task_completed(self, task):
        bot_tasks_executed.labels(task=str(task), state="success").inc()

    @commands.Cog.listener("on_authbot_task_failed")
    async def on_authbot_task_failed(self, task, args, kwargs, error):
        bot_tasks_executed.labels(task=str(task), state="failed").inc()
        if DISCORD_BOT_SEND_FAILURE_MESSAGES and DISCORD_BOT_FAILURE_MESSAGES_CHANNEL:
            message = [f"Bot Task Failed <{error}>"]
            message.append(f"ARGS: ```\n{json.dumps(args)[0:1000]}\n```")
            message.append(f"KWARGS: ```\n{json.dumps(kwargs)[0:1000]}\n```")
            if isinstance(error, HTTPException):
                if error.code == 429:
                    logger.error(message)
                    # do not try to send a message we are at capacity for doing stuff...
                    return
            send_message(message="\n".join(message),
                         channel_id=DISCORD_BOT_FAILURE_MESSAGES_CHANNEL)


def setup(bot):
    bot.add_cog(PromExporter(bot))
