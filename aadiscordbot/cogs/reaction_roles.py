import logging

from discord.ext import commands
from discord.utils import get

from allianceauth.services.modules.discord.models import DiscordUser

from aadiscordbot.cogs.utils.decorators import sender_has_perm

from ..models import ReactionRoleBinding, ReactionRoleMessage

logger = logging.getLogger(__name__)


class Reactions(commands.Cog):
    """
    Auth Roles as reaction roles. With optional Public Access at a message level.
    """

    def __init__(self, bot):
        self.bot = bot

    async def clean_emojis(self, payload):
        gld = get(self.bot.guilds, id=payload.guild_id)
        chan = gld.get_channel(payload.channel_id)
        msg = await chan.fetch_message(payload.message_id)
        rr_binds = ReactionRoleBinding.objects.filter(
            message=payload.message_id
        ).values_list('emoji_text', flat=True)
        for e in msg.reactions:
            if isinstance(e.emoji, str):
                em = e.emoji.encode('utf-8')
                es = e.emoji
                if str(em) not in rr_binds and es not in rr_binds:
                    async for u in e.users():
                        await e.remove(u)
            else:
                em = e.emoji.name.encode('utf-8')
                es = e.emoji.name
                if str(em) not in rr_binds and es not in rr_binds:
                    async for u in e.users():
                        await e.remove(u)

    @commands.command(pass_context=True)
    @sender_has_perm('aadiscordbot.manage_reactions')
    async def rr(self, ctx):
        await ReactionRoleMessage.objects.acreate(
            message=ctx.message.id, name=f"{ctx.message.channel.name} RR Message {ctx.message.id}")
        return await ctx.message.add_reaction("👍")

    @commands.Cog.listener("on_raw_reaction_add")
    async def add_react_listener(self, payload):
        """
            add role or group
        """
        if payload.user_id == self.bot.user.id:
            return True
        try:
            rr_msg = ReactionRoleMessage.objects.aget(
                message=payload.message_id)
            # do we have a binding?
            emoji = payload.emoji.name.encode('utf-8')
            if payload.emoji.id is not None:
                emoji = payload.emoji.id
            try:
                rr_binds = ReactionRoleBinding.objects.aget(
                    message=rr_msg, emoji=emoji)
            except ReactionRoleBinding.DoesNotExist:
                try:
                    rr_binds = ReactionRoleBinding.objects.aget(
                        message=rr_msg, emoji=payload.emoji.name)
                except Exception:
                    # admin adding new role?
                    if DiscordUser.objects.get(uid=payload.user_id).user.has_perm("aadiscordbot.manage_reactions"):
                        gld = get(self.bot.guilds, id=payload.guild_id)
                        chan = gld.get_channel(payload.channel_id)
                        msg = await chan.fetch_message(payload.message_id)
                        ReactionRoleBinding.objects.create(
                            message=rr_msg, emoji=emoji, emoji_text=payload.emoji.name.encode('utf-8'))
                        await msg.add_reaction(payload.emoji)
                        return await self.clean_emojis(payload)
            if rr_binds.group:
                try:
                    user = DiscordUser.objects.aget(uid=payload.user_id)
                    user = user.user
                    if rr_binds.group not in user.groups.all():
                        user.groups.add(rr_binds.group)
                except DiscordUser.DoesNotExist:
                    if rr_msg.non_auth_users:
                        try:
                            gld = get(self.bot.guilds, id=payload.guild_id)
                            role = get(gld.roles, name=rr_binds.group.name)
                            user = get(gld.members, id=payload.user_id)
                            await user.add_roles(role)
                        except AttributeError:
                            pass  # No group or user or guild. zero fks given
                    return await self.clean_emojis(payload)
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
            rr_msg = ReactionRoleMessage.objects.aget(
                message=payload.message_id)
            # do we have a binding?
            emoji = payload.emoji.name.encode('utf-8')
            if payload.emoji.id is not None:
                emoji = payload.emoji.id
            try:
                rr_binds = ReactionRoleBinding.objects.get(
                    message=rr_msg, emoji=emoji)
            except ReactionRoleBinding.DoesNotExist:
                try:
                    rr_binds = ReactionRoleBinding.objects.get(
                        message=rr_msg, emoji=payload.emoji.name)
                except ReactionRoleBinding.DoesNotExist:
                    return await self.clean_emojis(payload)
            try:
                user = DiscordUser.objects.get(uid=payload.user_id)
                user = user.user
                if rr_binds.group:
                    if rr_binds.group in user.groups.all():
                        user.groups.remove(rr_binds.group)
            except DiscordUser.DoesNotExist:
                if rr_msg.non_auth_users:
                    try:
                        gld = get(self.bot.guilds, id=payload.guild_id)
                        role = get(gld.roles, name=rr_binds.group.name)
                        user = get(gld.members, id=payload.user_id)
                        await user.remove_roles(role)
                    except AttributeError:
                        pass  # No group or user or guild. zero fks given
                return await self.clean_emojis(payload)
            await self.clean_emojis(payload)
        except ReactionRoleMessage.DoesNotExist:
            pass


def setup(bot):
    bot.add_cog(Reactions(bot))
