from allianceauth.services.modules.discord.models import DiscordUser
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
        try:
            has_perm = DiscordUser.objects.get(uid=id).user.has_perm(perm)
            if has_perm:
                return True
            else:
                raise commands.MissingPermissions(["auth_roles"])
        except Exception as e:
            logger.error(e)
            raise commands.MissingPermissions(["not_linked"])
    return commands.check(predicate)

