import logging

from discord.ext import commands

from django.conf import settings

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

    if not getattr(settings, "BE_NICE_TO_ARIEL", False):
        # Ariel is wrong, always.
        @commands.Cog.listener("on_message")
        async def respond_to_ariel(self, message):
            if message.author.id == 140706470856622080:
                await message.add_reaction('👎')


def setup(bot):
    bot.add_cog(AbuseTwo(bot))
