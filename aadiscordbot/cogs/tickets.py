# Cog Stuff
import logging
from typing import Optional

import discord
from discord import ChannelType, Embed, Message, command, ui
from discord.ext import commands

# AA Contexts
from django.conf import settings
from django.utils import timezone

from .. import models

logger = logging.getLogger(__name__)


def get_groups():
    groups = models.TicketGroups.get_solo().groups.all().order_by('name')
    out = []
    for g in groups:
        out.append(
            discord.SelectOption(
                label=f"{g.name}"
            )
        )
    return out


class TicketDropdown(discord.ui.Select):
    """
        Group Dropdown for discord message to summon a private help channel.
    """

    def __init__(self):
        super().__init__(
            placeholder="Who do you need help from?",
            options=get_groups(),
        )

    async def callback(self, interaction: discord.Interaction):
        sup_channel = models.TicketGroups.get_solo().ticket_channel.channel
        ch = interaction.guild.get_channel(sup_channel)
        grp = discord.utils.get(interaction.guild.roles, name=self.values[0])
        th = await ch.create_thread(name=f"{interaction.user.display_name} | {self.values[0]} | {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                                    auto_archive_duration=10080,
                                    type=discord.ChannelType.private_thread,
                                    reason=None)
        msg = f"<@{interaction.user.id}> needs help!, Someone from <@&{grp.id}> will get in touch soon!"
        embd = Embed(title="Private Thread Guide",
                     description="To add a person to this thread simply `@ping` them. This works with `@groups` as well to bulk add people to the channel. Use wisely, abuse will not be tolerated.\n\nThis is a beta feature if you experience issues please contact the admins. :heart:")
        await th.send(msg, embed=embd)
        await interaction.response.send_message(content="Ping in the thread created for urgent help!", view=None, ephemeral=True)


class HelpView(ui.View):
    """
        View for picking a group to assign a help thread too
    """

    def __init__(self):
        super().__init__(TicketDropdown())


class HelpCog(commands.Cog):
    """
        Help Ticket Cog Things
    """

    def __init__(self, bot):
        self.bot = bot

    @command(name='help', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def slash_halp(
        self,
        ctx,
    ):
        """
            Help me authbot i dont know who to ping!
        """
        await ctx.defer(ephemeral=True)
        return await ctx.respond(view=HelpView())

    @command(name='close_ticket', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def slash_close(
        self,
        ctx,
    ):
        """
            Mark help thread as completed and archive it!
        """
        ch = ctx.channel
        if ch.type != ChannelType.private_thread:
            return await ctx.respond("Not a private thread!", ephemeral=True)
        await ctx.defer()
        embd = Embed(title="Thread Marked Complete",
                     description=f"{ctx.user.display_name} has marked this thread as completed. To reopen simply start chatting again.")
        await ctx.respond(embed=embd)
        return await ch.archive()

    @commands.message_command(name="Create Help Ticket", guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def reverse_halp(self, ctx, message: Message):
        sup_channel = models.TicketGroups.get_solo().ticket_channel.channel
        ch = message.guild.get_channel(sup_channel)
        files = []
        for a in message.attachments:
            files.append(a.proxy_url)
        _f = "\n".join(files)

        th = await ch.create_thread(name=f"{message.author.display_name} | {message.id} | {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                                    #message=f"Ping in here if your request is urgent!",
                                    auto_archive_duration=10080,
                                    type=discord.ChannelType.private_thread,
                                    reason=None)
        msg = f"hi, <@{message.author.id}>, <@{ctx.author.id}> wants clarification on this message\n\n```{message.content}```\n\n{message.jump_url}\n{_f}"
        embd = Embed(title="Private Thread Guide",
                     description="To add a person to this thread simply `@ping` them. This works with `@groups` as well to bulk add people to the channel. Use wisely, abuse will not be tolerated.")

        await th.send(msg, embed=embd)


def setup(bot):
    bot.add_cog(HelpCog(bot))
