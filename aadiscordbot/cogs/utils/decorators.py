from allianceauth.services.modules.discord.models import DiscordUser
from aadiscordbot import app_settings
from discord.ext import commands
import functools
import os

import logging
logger = logging.getLogger(__name__)


# i dont want to do this, but the below object get wont work without it, investigate.
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


def sender_has_perm(perm):
    def predicate(ctx):
        id = ctx.message.author.id
        if id in app_settings.get_admins():
            return True
        try:
            has_perm = DiscordUser.objects.get(uid=id).user.has_perm(perm)
            if has_perm:
                return True
            if id in app_settings.get_admins():
                return True
            else:
                raise commands.MissingPermissions(["auth_roles"])
        except Exception as e:
            logger.error(e)
            raise commands.MissingPermissions(["not_linked"])
    return commands.check(predicate)


def sender_is_admin():
    def predicate(ctx):
        id = ctx.message.author.id
        if id in app_settings.get_admins():
            return True
        else:
            raise commands.MissingPermissions(["Admin Array"])
    return commands.check(predicate)


def message_in_channels(channels: list):
    def predicate(ctx):
        channel = ctx.message.channel
        if channel in channels:
            return True
        else:
            raise commands.MissingPermissions(["Channel Array"])
    return commands.check(predicate)