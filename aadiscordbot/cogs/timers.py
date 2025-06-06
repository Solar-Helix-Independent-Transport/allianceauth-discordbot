import datetime
import logging

from discord.colour import Color
from discord.embeds import Embed
from discord.ext import commands

from django.conf import settings
from django.utils import timezone

from allianceauth.timerboard.models import Timer

from aadiscordbot.app_settings import timerboard_active
from aadiscordbot.cogs.utils.decorators import message_in_channels

logger = logging.getLogger(__name__)


class Timers(commands.Cog):
    """
    TimerBoard Stuffs!
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @message_in_channels(settings.ADMIN_DISCORD_BOT_CHANNELS)
    async def timer(self, ctx):
        """
        Gets the Next Timer!
        :param ctx:
        :return:
        """
        next_timer = Timer.objects.filter(
            corp_timer=False,
            eve_time__gte=datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
        ).afirst()
        embed = Embed(title="Next Timer")
        embed.description = next_timer.details
        if next_timer.objective == "Friendly":
            embed.colour = Color.blue()
        elif next_timer.objective == "Hostile":
            embed.colour = Color.red()
        else:
            embed.colour = Color.white()
        try:
            embed.set_footer(text="Added By {}".format(
                next_timer.eve_character.character_name))
        except Exception as e:
            logger.error(e)
            pass

        embed.add_field(
            name="Structure:",
            value=next_timer.structure
        )
        embed.add_field(
            name="Location:",
            value=f"{next_timer.system} - {next_timer.planet_moon}"
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
    else:
        logger.debug("Timerboard not installed")
