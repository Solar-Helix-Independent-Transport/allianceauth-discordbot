# Cog Stuff
from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color
from django.conf import settings

from aadiscordbot.app_settings import get_site_url, timezones_active

from datetime import datetime
import pytz
import re

import logging
import pendulum
import traceback
logger = logging.getLogger(__name__)


class Time(commands.Cog):
    """
    A series of Time tools
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def time(self, ctx):
        """
        Returns EVE Time
        """
        await ctx.trigger_typing()

        url = None
        if timezones_active():
            url = get_site_url() + "/timezones/"

        message = '**Current EVE Time:** ' + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        if url is not None:
            message += '\n' + url

        return await ctx.send(message)


def setup(bot):
    bot.add_cog(Time(bot))
