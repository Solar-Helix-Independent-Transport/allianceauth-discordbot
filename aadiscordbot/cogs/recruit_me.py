# Cog Stuff
import logging

import discord
# AA-Discordbot
from discord.embeds import Embed
from discord.ext import commands

# AA Contexts
from django.conf import settings
from django.utils import timezone

from .. import app_settings

logger = logging.getLogger(__name__)


class RecruitMe(commands.Cog):
    """
    Thread Tools for recruiting!
    """

    def __init__(self, bot):
        self.bot = bot

    async def open_ticket(
        self,
        ctx: discord.Interaction,
        member: discord.Member
    ):
        sup_channel = settings.RECRUIT_CHANNEL_ID
        ch = ctx.guild.get_channel(sup_channel)
        th = await ch.create_thread(
            name=f"{member.display_name} | {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            auto_archive_duration=10080,
            type=discord.ChannelType.private_thread,
            reason=None
        )
        msg = (f"<@{member.id}> is hunting for a recruiter!\n\n"
               f"Someone from <@&{settings.RECRUITER_GROUP_ID}> will get in touch soon!")
        embd = Embed(title="Private Thread Guide",
                     description="To add a person to this thread simply `@ping` them. This works with `@groups` as well to bulk add people to the channel. Use wisely, abuse will not be tolerated.\n\nThis is a beta feature if you experience issues please contact the admins. :heart:")
        await th.send(msg, embed=embd)
        await ctx.response.send_message(content="Recruitment thread created!", view=None, ephemeral=True)

    @commands.slash_command(
        name='recruit_me',
        guild_ids=app_settings.get_all_servers()
    )
    async def slash_halp(
        self,
        ctx,
    ):
        """
            Get hold of a recruiter
        """
        await self.open_ticket(ctx, ctx.user)

    @commands.message_command(
        name="Create Recruitment Thread",
        guild_ids=app_settings.get_all_servers()
    )
    async def reverse_recruit_msg_context(
        self,
        ctx,
        message
    ):
        """
            Help a new guy get recruiter
        """
        await self.open_ticket(ctx, message.author)

    @commands.user_command(
        name="Recruit Member",
        guild_ids=app_settings.get_all_servers()
    )
    async def reverse_recruit_user_context(
        self, ctx, user
    ):
        """
            Help a new guy get recruiter
        """
        await self.open_ticket(ctx, user)


def setup(bot):
    bot.add_cog(RecruitMe(bot))
