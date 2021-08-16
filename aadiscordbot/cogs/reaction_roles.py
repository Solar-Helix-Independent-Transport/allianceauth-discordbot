from discord.ext import commands
from discord.utils import get
from .. import app_settings 
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

    async def clean_emojis(self, payload):
        logger.debug("Ensuring emojis are tidy")
        gld = get(self.bot.guilds, id=payload.guild_id)
        chan = gld.get_channel(payload.channel_id)
        msg = await chan.fetch_message(payload.message_id)
        rr_binds = ReactionRoleBinding.objects.filter(message=payload.message_id).values_list('emoji_text', flat=True)
        for e in msg.reactions:
            if isinstance(e.emoji, str):
                if e.emoji not in rr_binds:
                    async for u in e.users():
                        await e.remove(u)
            else:
                if e.emoji.name not in rr_binds:
                    async for u in e.users():
                        await e.remove(u)


    @commands.Cog.listener("on_raw_reaction_add")
    async def add_react_listener(self, payload):
        """
            add role or group
        """
        if payload.user_id == self.bot.user.id:
            return True
        try: 
            rr_msg = ReactionRoleMessage.objects.get(message=payload.message_id)
            # do we have a binding?
            emoji = payload.emoji.name.encode('utf-8')
            logger.debug("got emoji on known message")
            if payload.emoji.id is not None:
                emoji = payload.emoji.id
            try:
                rr_binds = ReactionRoleBinding.objects.get(message=rr_msg, emoji=emoji)
                logger.debug("got known emoji")
                user = DiscordUser.objects.get(uid=payload.user_id).user
                if rr_binds.group:
                    if rr_binds.group not in user.groups.all():
                        user.groups.add(rr_binds.group)
            except ReactionRoleBinding.DoesNotExist:
                # admin adding new role?
                logger.debug("got unknown emoji")
                if payload.user_id in app_settings.DISCORD_BOT_ADMIN_USER:
                    logger.debug("user can add, adding new emoji")
                    gld = get(self.bot.guilds, id=payload.guild_id)
                    chan = gld.get_channel(payload.channel_id)
                    msg = await chan.fetch_message(payload.message_id)
                    ReactionRoleBinding.objects.create(message=rr_msg, emoji=emoji, emoji_text=payload.emoji.name)
                    await msg.add_reaction(payload.emoji)

            await self.clean_emojis(payload)
        except ReactionRoleMessage.DoesNotExist:
            pass

    @commands.Cog.listener("on_raw_reaction_remove")
    async def rem_react_listener(self, payload):
        """
            rem role or group
        """
        if payload.user_id == self.bot.client_id:
            return True
        try:
            rr_msg = ReactionRoleMessage.objects.get(message=payload.message_id)
            # do we have a binding?
            logger.debug("known messaage, removing user from group.")
            emoji = payload.emoji.name.encode('utf-8')
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
            await self.clean_emojis(payload)
        except ReactionRoleMessage.DoesNotExist:
            pass


def setup(bot):
    bot.add_cog(Reactions(bot))
