# Cog Stuff
import logging

import discord
from discord import ChannelType, Embed, Message, command, ui
from discord.commands import option
from discord.ext import commands

# AA Contexts
from django.utils import timezone

from aadiscordbot import app_settings

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


THREAD_EMBED = Embed(
    title="Private Thread Guide",
    description=(
        "To add a person to this thread simply `@ping` them. "
        "This works with `@groups` as well to bulk add people "
        "to the channel. Use wisely, abuse will not be tolerated."
    )
)


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
        sup_channel = models.TicketGroups.get_solo(
        ).get_channel_for_server(interaction.guild_id)
        if sup_channel:
            ch = interaction.guild.get_channel(sup_channel)
            grp = discord.utils.get(interaction.guild.roles, name=self.values[0])
            if grp is None:
                return await interaction.response.edit_message(
                    content=(
                        "That group is not found in this server?"
                    ),
                    view=None,
                )
            th = await ch.create_thread(
                name=(
                    f"{interaction.user.display_name} | "
                    f"{self.values[0]} | {timezone.now().strftime('%Y-%m-%d %H:%M')}"
                ),
                auto_archive_duration=10080,
                type=discord.ChannelType.private_thread,
                reason=None
            )
            msg = (
                f"<@{interaction.user.id}> needs help!, Someone from"
                f" <@&{grp.id if grp else 0}> will get in touch soon!"
            )
            await th.send(msg, embed=THREAD_EMBED)
            await interaction.response.edit_message(
                content=(
                    f"Check the thread created! {th.mention} "
                    "Ping in the thread for urgent help!"
                ),
                view=None,
            )
        else:
            await interaction.response.edit_message(
                content=(
                    "No Channel found in the configuration for this server? Contact the admins."
                ),
                view=None,
            )


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

    @command(name='help', guild_ids=app_settings.get_all_servers())
    async def slash_halp(
        self,
        ctx,
    ):
        """
            Help me authbot i dont know who to ping!
        """
        await ctx.defer(ephemeral=True)
        return await ctx.respond(view=HelpView())

    @command(name='close_ticket', guild_ids=app_settings.get_all_servers())
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
        embd = Embed(
            title="Thread Marked Complete",
            description=(
                f"{ctx.user.display_name} has marked this thread as completed."
                " To reopen simply start chatting again."
            )
        )
        await ctx.respond(embed=embd)
        return await ch.archive()

    @command(name='help_targeted', guild_ids=app_settings.get_all_servers())
    @option("character", description="What Character to add to the ticket")
    @option("group", description="What Group to add to the ticket ")
    async def slash_reverse_help(
        self,
        interaction,
        character: discord.User = None,
        group: discord.Role = None
    ):
        """
            Open a ticket and drag people in by force!
        """
        if character is None and group is None:
            return await interaction.response.send_message(
                content="You need to pick someone to add...",
                view=None,
                ephemeral=True)

        mentions = []
        names = []
        if character is not None:
            mentions.append(f"{character.mention} ")
            names.append(character.display_name)

        if group is not None:
            mentions.append(f"{group.mention} ")
            names.append(group.name)

        mentions = ", ".join(mentions)
        names = ", ".join(names)
        sup_channel = models.TicketGroups.get_solo().ticket_channel.channel
        ch = interaction.guild.get_channel(sup_channel)

        th = await ch.create_thread(
            name=(
                f"{interaction.user.display_name} |"
                f" {names} | {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            ),
            auto_archive_duration=10080,
            type=discord.ChannelType.private_thread,
            reason=None)
        msg = f"<@{interaction.user.id}> has a question for: "
        mentions = []
        if character is not None:
            mentions.append(f"{character.mention} ")

        if group is not None:
            mentions.append(f"{group.mention} ")

        msg += ", ".join(mentions)

        await th.send(msg, embed=THREAD_EMBED)
        await interaction.response.send_message(
            content=f"Check the thread created! {th.mention}",
            view=None,
            ephemeral=True
        )

    @commands.message_command(
        name="Create Help Ticket",
        guild_ids=app_settings.get_all_servers()
    )
    async def reverse_halp(self, ctx, message: Message):
        sup_channel = models.TicketGroups.get_solo().ticket_channel.channel
        ch = message.guild.get_channel(sup_channel)
        files = []
        for a in message.attachments:
            files.append(a.proxy_url)
        _f = "\n".join(files)

        th = await ch.create_thread(
            name=(
                f"{message.author.display_name} | "
                f"{message.id} | {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            ),
            auto_archive_duration=10080,
            type=discord.ChannelType.private_thread,
            reason=None
        )
        msg = (
            f"hi, <@{message.author.id}>, <@{ctx.author.id}> "
            "wants clarification on this message\n\n"
            f"```{message.content}```\n\n{message.jump_url}\n{_f}"
        )
        await th.send(msg, embed=THREAD_EMBED)


def setup(bot):
    bot.add_cog(HelpCog(bot))
