# Cog Stuff
import logging
from typing import Optional

import discord
from discord import Embed, command, ui
from discord.ext import commands

# AA Contexts
from django.conf import settings
from django.utils import timezone

from .. import models

logger = logging.getLogger(__name__)


def get_groups():
    groups = models.TicketGroups.get_solo().groups.all()
    out = []
    for g in groups:
        out.append(
            discord.SelectOption(
                label=f"{g.name}"
            )
        )
    return out


class HelpView(ui.View):
    """
        View for picking a group to assign a help thread too
    """

    embed_text = None
    message_text = ""
    created = None

    def __init__(self,
                 *items: discord.ui.Item,
                 timeout: Optional[float] = 60*60,  # 24h from last click
                 embed: Optional[Embed] = None,
                 message: Optional[str] = None,
                 bot=None
                 ):
        if embed:
            if isinstance(embed, dict):
                self.embed_text = Embed.from_dict(embed)
            elif isinstance(embed, Embed):
                self.embed_text = embed
        if message:
            self.message_text = message
        self.bot = bot
        self.created = timezone.now()

        super().__init__(*items, timeout=timeout)

    # a custom_id must be set
    @discord.ui.select(placeholder="Who do you need help from?", options=get_groups())
    async def select_callback(self, select, interaction):
        sup_channel = models.TicketGroups.get_solo().ticket_channel.channel
        ch = interaction.guild.get_channel(sup_channel)
        grp = discord.utils.get(interaction.guild.roles, name=select.values[0])
        th = await ch.create_thread(name=f"Help {interaction.user}",
                                    # message=f"Ping in here if your request is urgent <@{interaction.user.id}>, Someone from <#{grp.id}> will be here soon!",
                                    auto_archive_duration=10080,
                                    type=discord.ChannelType.private_thread,
                                    reason=None)
        msg = f"<@{interaction.user.id}> needs help!, Someone from <@&{grp.id}> will get in touch soon!"
        embd = Embed(title="Private Thread Guide",
                     description="To add a person to this thread simply @ping them. This works with @groups as well to bulk add people to the channel. Use it wisely.\n\nThis is a beta bot feature if you experience issues please contact the server admins. :heart:")
        await th.send(msg, embed=embd)
        await interaction.response.edit_message(content="Ping in the thread created for urgent help!", view=None)

    async def on_timeout(self) -> None:
        await super().on_timeout()


class HelpCog(commands.Cog):
    """
        Compliance Related thingies
    """

    def __init__(self, bot):
        self.bot = bot

    @command(name='help', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def slash_halp(
        self,
        ctx,
    ):
        """
            Halp me authbot i dont know who to ping!
        """
        await ctx.defer(ephemeral=True)
        return await ctx.respond(view=HelpView())


def setup(bot):
    bot.add_cog(HelpCog(bot))
