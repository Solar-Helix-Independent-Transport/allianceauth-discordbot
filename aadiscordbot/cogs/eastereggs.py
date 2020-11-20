import logging
import pendulum
import traceback
import re

import discord

from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color
from django.conf import settings

from aadiscordbot.app_settings import get_site_url

from allianceauth.services.modules.discord.models import DiscordUser

logger = logging.getLogger(__name__)

class EasterEggs(commands.Cog):
    """
    Stupid commands that don't belong anywhere
    These will not appear in Help menus
    Have limited to no real use
    I was bored
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, hidden=True)
    async def happybirthday(self, ctx):
        """
        Takes one Discord User as an argument, Wishes this user a happy birthday
        If no user is passed, responds to the context user
        "Useful" to verify the bot is alive and functioning
        """
        await ctx.trigger_typing()

        birthday_user = ctx.message.content[15:]

        if birthday_user == "":
            birthday_user = ctx.message.author.mention
        else:
            pass

        payload = f"Happy Birthday {birthday_user}"
        return await ctx.send(payload)

def setup(bot):
    bot.add_cog(EasterEggs(bot))
