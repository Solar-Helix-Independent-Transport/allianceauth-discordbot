import importlib
import io
import logging
import warnings
from datetime import timedelta

from discord import Embed, File
from discord.ext import tasks
from discord.ext.commands import Bot

import django
from django.conf import settings
from django.utils import timezone

from aadiscordbot.cogs.utils.exceptions import NotAuthenticated

logger = logging.getLogger(__name__)

GUILD_ID = settings.DISCORD_GUILD_ID


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
            # logger.debug(f"Rate Limit hit! Re Queueing `{task}`")
        else:
            try:
                await task(bot, *args, **kwargs)
                bot.statistics.add_task(task.__name__)
                bot.dispatch("authbot_task_completed", task.__name__)
            except Exception as e:
                bot.dispatch("authbot_task_failed",
                             task.__name__, args, kwargs, e)
                logger.error(
                    f"Failed to run task {task} {args} {kwargs} {e}", exc_info=True)
    else:
        run_tasks.stop()
    django.db.close_old_connections()


async def send_channel_message_by_discord_id(bot, channel_id, message, embed=None, view_class=None, view_args=[], view_kwargs={}, file=None, files=None):

    logger.debug(f"Sending Channel Message to Discord ID {channel_id}")

    e = None
    v = None
    f = None
    fls = None

    if embed:
        e = Embed.from_dict(embed)

    if file:
        f = File(io.BytesIO(file[0]), file[1])

    if files:
        fls = []
        for _f in files:
            fls.append(File(io.BytesIO(_f[0]), _f[1]))

    if view_class:
        m = ".".join(view_class.split(".")[:-1])
        c = view_class.split(".")[-1]
        my_module = importlib.import_module(m)
        Viewclass = getattr(my_module, c)
        v = Viewclass(*view_args, **view_kwargs)

    await bot.get_channel(channel_id).send(message, embed=e, view=v, file=f, files=fls)


async def send_channel_message(bot, channel_id, message, embed=False):
    warnings.warn(
        "send_channel_message is deprecated, use send_channel_message_by_discord_id instead",
        DeprecationWarning
    )
    await send_channel_message_by_discord_id(bot, channel_id, message, embed=embed)


async def send_direct_message_by_discord_id(bot, discord_user_id, message, embed=False):
    logger.debug(f"Sending DM to Discord ID {discord_user_id}")

    user_object = await bot.fetch_user(discord_user_id)
    if user_object.can_send():
        await user_object.create_dm()
        if embed:
            e = Embed.from_dict(embed)
            await user_object.send(message, embed=e)
        else:
            await user_object.send(message)
    else:
        logger.error(
            f"Unable to DM discord_user_id={discord_user_id} {user_object}")


async def send_direct_message(bot, discord_user_id, message, embed=False):
    warnings.warn(
        "send_direct_message is deprecated, use send_direct_message_by_discord_id instead",
        DeprecationWarning
    )
    await send_direct_message_by_discord_id(bot, discord_user_id, message, embed=embed)


async def send_direct_message_by_user_id(bot, user_pk, message, embed=False):
    # App isn't loaded when this file is imported, so importing here
    from django.contrib.auth.models import User

    from .utils.auth import get_discord_user_id

    logger.debug(f"Sending DM to User ID {user_pk}")
    user = User.objects.get(pk=user_pk)
    try:
        discord_user_id = get_discord_user_id(user)
        user_object = await bot.fetch_user(discord_user_id)
        if user_object.can_send():
            await user_object.create_dm()
            if embed:
                e = Embed.from_dict(embed)
                await user_object.send(message, embed=e)
            else:
                await user_object.send(message)
        else:
            logger.error(f"Unable to DM user_pk={user_pk} {user_object}")

    except NotAuthenticated:
        logger.debug(f"No discord account on record for user_pk={user_pk}")


async def pop_user_group_cache(bot, user_pk):
    logger.debug(f"Refreshing user cache {user_pk}")
    user = bot.get_guild(int(GUILD_ID)).get_member(user_pk)
    r = user.roles[-1]
    await user.remove_roles(r)
    await user.add_roles(r)
    logger.info(
        f"Removed and added '{r}' to {user} to try and bust the invalid cache")


async def run_task_function(bot, function, task_args, task_kwargs):
    mod_name, func_name = function.rsplit('.', 1)
    mod = importlib.import_module(mod_name)
    func = getattr(mod, func_name)
    await func(bot, *task_args, **task_kwargs)
