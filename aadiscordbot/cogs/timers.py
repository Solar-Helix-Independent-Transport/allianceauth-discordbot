import logging
import pendulum
import traceback

import discord

from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color

import datetime
from django.utils import timezone

#log = logging.getLogger(__name__)

from allianceauth.timerboard.models import Timer

class Timers(commands.Cog):
    """
    TimerBoard Stuffs!
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def timer(self, ctx):
        """
        Gets the Next Timer!
        :param ctx:
        :return:
        """
        next_timer = Timer.objects.filter(corp_timer=False,
                                          eve_time__gte=datetime.datetime.utcnow().replace(tzinfo=timezone.utc)).first()
        time_until = pendulum.now(tz="UTC").diff_for_humans(
                            next_timer.eve_time , absolute=True
                        )
        embed = Embed(title="Next Timer")
        embed.description = next_timer.details
        if next_timer.objective == "Friendly":
            embed.colour = Color.blue()
        elif next_timer.objective == "Hostile":
            embed.colour = Color.red()
        else:
            embed.colour = Color.white()
        try:
            embed.set_footer(text="Added By {0}".format(next_timer.eve_character.character_name))
        except:
            pass

        embed.add_field(
            name="Structure:",
            value=next_timer.structure
        )
        embed.add_field(
            name="Location:",
            value="{0} - {1}".format(next_timer.system, next_timer.planet_moon)
        )
        embed.add_field(
            name="Eve Time:",
            value=next_timer.eve_time.strftime("%Y-%m-%d %H:%M"),
            inline=False
        )
        return await ctx.send(embed=embed)


def setup(bot):
    if timerboard_active():
        bot.add_cog(Timers(bot))
    else
        logger.debug("Timerboard not installed")
