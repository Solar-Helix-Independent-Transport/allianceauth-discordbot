from discord.ext import commands
from discord.utils import get

import logging
logger = logging.getLogger(__name__)

from ..models import ReactionRoleBinding, ReactionRoleMessage
from allianceauth.services.modules.discord.models import DiscordUser

class Reactions(commands.Cog):
    """
    Auth Roles as reaction roles

    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_raw_reaction_add")
    async def add_react_listener(self, payload):
        """
            add role or group
        """
        try: 
            rr_msg = ReactionRoleMessage.objects.get(message=payload.message_id)
            # do we have a binding?
            emoji = payload.emoji.name
            if payload.emoji.id is not None:
                emoji = payload.emoji.id
            try:
                rr_binds = ReactionRoleBinding.objects.get(message=rr_msg, emoji=emoji)
                user = DiscordUser.objects.get(uid=payload.user_id).user
                if rr_binds.group:
                    if rr_binds.group not in user.groups.all():
                        user.groups.add(rr_binds.group)
            except ReactionRoleBinding.DoesNotExist:
                # admin adding new role?
                if DiscordUser.objects.get(uid=payload.user_id).user.has_perm("reaction_role_message.manage_reactions"):
                    gld = get(self.bot.guilds, id=payload.guild_id)
                    chan = gld.get_channel(payload.channel_id)
                    msg = await chan.fetch_message(payload.message_id)
                    await msg.add_reaction(payload.emoji)
                    ReactionRoleBinding.objects.create(message=rr_msg, emoji=emoji, emoji_text=payload.emoji.name)
        except ReactionRoleMessage.DoesNotExist:
            pass


    @commands.Cog.listener("on_raw_reaction_remove")
    async def rem_react_listener(self, payload):
        """
            rem role or group
        """
        try:
            rr_msg = ReactionRoleMessage.objects.get(message=payload.message_id)
            # do we have a binding?
            emoji = payload.emoji.name
            if payload.emoji.id is not None:
                emoji = payload.emoji.id
            try:
                rr_binds = ReactionRoleBinding.objects.get(message=rr_msg, emoji=emoji)
                user = DiscordUser.objects.get(uid=payload.user_id).user
                if rr_binds.group:
                    if rr_binds.group in user.groups.all():
                        user.groups.remove(rr_binds.group)
            except ReactionRoleBinding.DoesNotExist:
                pass
        except ReactionRoleMessage.DoesNotExist:
            pass


def setup(bot):
    bot.add_cog(Reactions(bot))
