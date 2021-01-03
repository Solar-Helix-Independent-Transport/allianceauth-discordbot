import logging
import warnings
from discord.utils import get
from discord.ext import tasks

logger = logging.getLogger(__name__)

@tasks.loop()
async def run_tasks(bot):
    if len(bot.tasks) > 0:
        task, args = bot.tasks.pop(0)
        await task(bot, args)
    else:
        run_tasks.stop()

async def send_channel_message_by_discord_id(bot, args):
    logger.debug("I am running a Send Channel Message Task")
    channel_id = int(args[0])
    await bot.get_channel(channel_id).send(args[1].strip("'"))

async def send_channel_message(bot, args):
    warnings.warn(
        "send_channel_message is deprecated, use send_channel_message_by_discord_id instead",
        DeprecationWarning
    )
    await send_channel_message_by_discord_id(bot, args)

async def send_direct_message_by_discord_id(bot, args):
    discord_user_id = int(args[0])
    logger.debug(f"Sending DM to Discord ID {discord_user_id}")

    channel = await bot.get_user(discord_user_id).create_dm()
    await channel.send(args[1].strip("'"))

async def send_direct_message(bot, args):
    warnings.warn(
        "send_direct_message is deprecated, use send_direct_message_by_discord_id instead",
        DeprecationWarning
    )
    await send_direct_message_by_discord_id(bot, args)

async def send_direct_message_by_user_id(bot, args):
    # App isn't loaded when this file is imported, so importing here
    from django.contrib.auth.models import User
    user_pk = int(args[0])
    logger.debug(f"Sending DM to User ID {user_pk}")
    user = User.objects.get(pk=user_pk)
    if hasattr(user, "discord"):
        discord_user_id = user.discord.uid
        channel = await bot.get_user(discord_user_id).create_dm()
        await channel.send(args[1].strip("'"))
    else:
        logger.debug(f"No discord account on record for user_pk={user_pk}")

