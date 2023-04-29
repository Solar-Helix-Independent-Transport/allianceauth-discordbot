import importlib
import logging
import warnings
from datetime import timedelta

from discord import Embed
from discord.ext import tasks
from discord.ext.commands import Bot
from discord.ui import View

import django
from django.utils import timezone

logger = logging.getLogger(__name__)


@tasks.loop()
async def run_tasks(bot: Bot):
    django.db.close_old_connections()

    if len(bot.tasks) > 0:
        task, args, kwargs = bot.tasks.pop(0)
        requeue_task = False
        if hasattr(bot, 'rate_limits'):
            if not bot.rate_limits.check_rate_limit(task.__name__):
                requeue_task = True
        if requeue_task:
            # timeout ( for now lets just add 1 second )
            timeout = 1
            eta = timezone.now() + timedelta(seconds=timeout)
            bot.pending_tasks.append((eta, (task, args, kwargs)))
            #logger.debug(f"Rate Limit hit! Re Queueing `{task}`")
        else:
            try:
                await task(bot, *args, **kwargs)
                bot.statistics.add_task(task.__name__)
                bot.dispatch("authbot_task_completed", task.__name__)
            except Exception as e:
                bot.dispatch("authbot_task_failed",
                             task.__name__, args, kwargs, e)
                logger.error(f"Failed to run task {task} {args} {kwargs} {e}")
    else:
        run_tasks.stop()
    django.db.close_old_connections()


async def send_channel_message_by_discord_id(bot, channel_id, message, embed=False, view_class=False, view_args=[], view_kwargs={}):
    logger.debug(f"Sending Channel Message to Discord ID {channel_id}")
    e = None
    v = None
    if embed:
        e = Embed.from_dict(embed)

    if view_class:
        m = ".".join(view_class.split(".")[:-1])
        c = view_class.split(".")[-1]
        my_module = importlib.import_module(m)
        Viewclass = getattr(my_module, c)
        v = Viewclass(*view_args, **view_kwargs)

    await bot.get_channel(channel_id).send(message, embed=e, view=v)


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
