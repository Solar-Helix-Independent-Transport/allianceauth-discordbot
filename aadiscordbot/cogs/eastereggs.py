import logging

from discord import User
from discord.ext import commands

from django.conf import settings

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

    @commands.slash_command(name='happybirthday')
    async def happybirthday(self, ctx,  user: User):
        """
        Takes one Discord User as an argument, Wishes this user a happy birthday
        If no user is passed, responds to the context user
        "Useful" to verify the bot is alive and functioning
        """
        await ctx.trigger_typing()
        return await ctx.respond(f"Happy Birthday {user.mention}")


def setup(bot):
    bot.add_cog(EasterEggs(bot))
