"""
"Time" cog for discordbot - https://github.com/pvyParts/allianceauth-discordbot
"""

import logging
from datetime import datetime

from discord.colour import Color
from discord.embeds import Embed
from discord.ext import commands

from django.conf import settings

logger = logging.getLogger(__name__)


class Time(commands.Cog):
    """
    A series of Time tools
    """

    def __init__(self, bot):
        self.bot = bot

    def build_embed(self):
        fmt_utc = "%H:%M:%S (UTC)\n%A %d. %b %Y"

        embed = Embed(title="Time")
        embed.colour = Color.green()

        embed.add_field(
            name="EVE Time",
            value=datetime.utcnow().strftime(fmt_utc),
            inline=False,
        )

        return embed

    @commands.command(pass_context=True)
    async def time(self, ctx):
        """
        Returns EVE Time
        """

        return await ctx.send(embed=self.build_embed())

    @commands.slash_command(name="time", guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def time_slash(self, ctx):
        """
        Returns EVE Time
        """

        return await ctx.respond(embed=self.build_embed())


def setup(bot):
    """
    setup the cog
    :param bot:
    """

    # Only load if there is no other Time cog loaded already
    # aa-timezones>=1.10.0 for example
    if bot.get_cog("Time") is None:
        bot.add_cog(Time(bot))
