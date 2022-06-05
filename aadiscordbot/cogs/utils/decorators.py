from allianceauth.services.modules.discord.models import DiscordUser
from aadiscordbot.app_settings import DISCORD_BOT_ADMIN_USER
from discord.ext import commands
import functools
import os

import logging
logger = logging.getLogger(__name__)


# i dont want to do this, but the below object get wont work without it, investigate.
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


def has_perm(id, perm: str):
    if id in DISCORD_BOT_ADMIN_USER:
        return True
    try:
        has_perm = DiscordUser.objects.get(uid=id).user.has_perm(perm)
        if has_perm:
            return True
        else:
            raise commands.MissingPermissions(["Missing Auth Permission"])
    except Exception as e:
        logger.error(e)
        raise commands.MissingPermissions(["Not Authenticated"])


def sender_has_perm(perm: str):
    """
    Permission Decorator: Does the user have x Django Permission
    """
    def predicate(ctx):
        return has_perm(ctx.message.author.id, perm)

    return commands.check(predicate)


def has_all_perms(id, perms: list):
    if id in DISCORD_BOT_ADMIN_USER:
        return True
    try:
        has_perm = DiscordUser.objects.get(uid=id).user.has_perms(perms)
        if has_perm:
            return True
        else:
            raise commands.MissingPermissions(["Missing Auth Permission"])
    except Exception as e:
        logger.error(e)
        raise commands.MissingPermissions(["Not Authenticated"])


def sender_has_all_perms(perms: list):
    """
    Permission Decorator: Does the user have x and y Django Permission
    """
    def predicate(ctx):
        return has_all_perms(ctx.message.author.id, perms)

    return commands.check(predicate)


def has_any_perm(id, perms: list):
    if id in DISCORD_BOT_ADMIN_USER:
        return True
    for perm in perms:
        try:
            has_perm = DiscordUser.objects.get(uid=id).user.has_perm(perm)
            if has_perm:
                return True
            if id in DISCORD_BOT_ADMIN_USER:
                return True
        except Exception as e:
            logger.error(e)
            raise commands.MissingPermissions(["Not Authenticated"])
    raise commands.MissingPermissions(["Missing Auth Permission"])


def sender_has_any_perm(perms: list):
    """
    Permission Decorator: Does the user have x or y Django Permission
    """
    def predicate(ctx):
        return has_any_perm(ctx.message.author.id, perms)

    return commands.check(predicate)


def is_admin(id):
    if id in DISCORD_BOT_ADMIN_USER:
        return True
    else:
        raise commands.MissingPermissions(["Not an Admin"])


def sender_is_admin():
    def predicate(ctx):
        return is_admin(ctx.message.author.id)
    return commands.check(predicate)


def in_channels(channel, channels):
    if channel in channels:
        return True
    else:
        raise commands.MissingPermissions(["Not an Allowed Channel"])


def message_in_channels(channels: list):
    def predicate(ctx):
        return in_channels(ctx.message.channel.id, channels)
    return commands.check(predicate)
