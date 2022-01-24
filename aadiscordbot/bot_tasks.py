import logging
import warnings
from discord.utils import get
from discord.ext import tasks
from discord import Embed
logger = logging.getLogger(__name__)

@tasks.loop()
async def run_tasks(bot):
    if len(bot.tasks) > 0:
        task, args, kwargs = bot.tasks.pop(0)
        await task(bot, *args, **kwargs)
    else:
        run_tasks.stop()

async def send_channel_message_by_discord_id(bot, channel_id, message, embed=False):
    logger.debug("I am running a Send Channel Message Task")
    if embed:
        e = Embed.from_dict(embed)
        await bot.get_channel(channel_id).send(message, embed=e)
    else:
        await bot.get_channel(channel_id).send(message)

async def send_channel_message(bot, channel_id, message, embed=False):
    warnings.warn(
        "send_channel_message is deprecated, use send_channel_message_by_discord_id instead",
        DeprecationWarning
    )
    await send_channel_message_by_discord_id(bot, channel_id, message, embed=embed)

async def send_direct_message_by_discord_id(bot, discord_user_id, message, embed=False):
    logger.debug(f"Sending DM to Discord ID {discord_user_id}")

    channel = await bot.get_user(discord_user_id).create_dm()
    if embed:
        e = Embed.from_dict(embed)
        await channel.send(message, embed=e)
    else:
        await channel.send(message)

async def send_direct_message(bot, discord_user_id, message, embed=False):
    warnings.warn(
        "send_direct_message is deprecated, use send_direct_message_by_discord_id instead",
        DeprecationWarning
    )
    await send_direct_message_by_discord_id(bot, discord_user_id, message, embed=embed)

async def send_direct_message_by_user_id(bot, user_pk, message, embed=False):
    # App isn't loaded when this file is imported, so importing here
    from django.contrib.auth.models import User
    logger.debug(f"Sending DM to User ID {user_pk}")
    user = User.objects.get(pk=user_pk)
    if hasattr(user, "discord"):
        discord_user_id = user.discord.uid
        channel = await bot.get_user(discord_user_id).create_dm()
        if embed:
            e = Embed.from_dict(embed)
            await channel.send(message, embed=e)
        else:
            await channel.send(message)
    else:
        logger.debug(f"No discord account on record for user_pk={user_pk}")

