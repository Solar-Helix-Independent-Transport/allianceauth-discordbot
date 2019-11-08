from allianceauth.services.modules.discord.models import DiscordUser
from discord.ext import commands
import functools

def sender_has_perm(perm):
    def predicate(ctx):
        id = ctx.message.author.id
        try:
            has_perm=DiscordUser.objects.get(uid=id).user.has_perm(perm)
            if has_perm:
                return True
            else:
                raise commands.MissingPermissions(["auth_roles"])
        except:
            raise commands.MissingPermissions(["not_linked"])
    return commands.check(predicate)
