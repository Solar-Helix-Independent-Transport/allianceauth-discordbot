from allianceauth.services.modules.discord.models import DiscordUser
from aadiscordbot.app_settings import DISCORD_BOT_ADMIN_USER
from discord.ext import commands
import functools
import os

import logging
logger = logging.getLogger(__name__)


# i dont want to do this, but the below object get wont work without it, investigate.
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


def sender_has_perm(perm: str):
    """
    Permission Decorator: Does the user have x Django Permission
    """
    def predicate(ctx):
        id = ctx.message.author.id
        if id in DISCORD_BOT_ADMIN_USER:
            return True
        try:
            has_perm = DiscordUser.objects.get(uid=id).user.has_perm(perm)
            if has_perm:
                return True
            if id in DISCORD_BOT_ADMIN_USER:
                return True
            else:
                raise commands.MissingPermissions(["Missing Auth Permission"])
        except Exception as e:
            logger.error(e)
            raise commands.MissingPermissions(["Not Authenticated"])
    return commands.check(predicate)


def sender_has_all_perms(perms: list):
    """
    Permission Decorator: Does the user have x and y Django Permission
    """
    def predicate(ctx):
        id = ctx.message.author.id
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
    return commands.check(predicate)


def sender_has_any_perm(perms: list):
    """
    Permission Decorator: Does the user have x or y Django Permission
    """
    def predicate(ctx):
        id = ctx.message.author.id
        if id in DISCORD_BOT_ADMIN_USER:
            return True
        for perm in perms:
            try:
                has_perm = DiscordUser.objects.get(uid=id).user.has_perm(perm)
                if has_perm:
                    return True
                if id in DISCORD_BOT_ADMIN_USER:
                    return True
                else:
                    raise commands.MissingPermissions(["Missing Auth Permission"])
            except Exception as e:
                logger.error(e)
                raise commands.MissingPermissions(["Not Authenticated"])
    return commands.check(predicate)


def sender_is_admin():
    def predicate(ctx):
        id = ctx.message.author.id
        if id in DISCORD_BOT_ADMIN_USER:
            return True
        else:
            raise commands.MissingPermissions(["Not an Admin"])
    return commands.check(predicate)


def message_in_channels(channels: list):
    def predicate(ctx):
        channel = ctx.message.channel.id
        if channel in channels:
            return True
        else:
            raise commands.MissingPermissions(["Not an Allowed Channel"])
    return commands.check(predicate)
