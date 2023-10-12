import logging

from discord.colour import Color
from discord.commands import SlashCommandGroup
from discord.embeds import Embed
from discord.ext import commands

from django.conf import settings

from aadiscordbot import __branch__, __version__
from aadiscordbot.app_settings import get_site_url

logger = logging.getLogger(__name__)


class AbuseTwo(commands.Cog):
    """
    Emojis for abusing reasons...!
    """

    def __init__(self, bot):
        self.bot = bot

    # Ariel is wrong, always.
    @commands.Cog.listener("on_message")
    async def respond_to_abusee(self, message):
        if message.author.id == settings.DISCORD_BOT_ABUSEE_ID:
            await message.add_reaction(getattr(settings, 'DISCORD_BOT_ABUSEE_EMOJI', '👎'))


def setup(bot):
    bot.add_cog(AbuseTwo(bot))
