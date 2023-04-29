import logging
from random import randrange

from discord.ext import commands

from django.conf import settings

from aadiscordbot import __branch__, __version__

logger = logging.getLogger(__name__)


class EightBall(commands.Cog):
    """
    All about me!
    """

    def __init__(self, bot):
        self.bot = bot

    def eightball(self):
        replies = [
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes definitely!",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Yes",
            "Signs point to yes",
            "Reply hazy, try again",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",
            "Don't count on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful",
        ]
        return replies[randrange(0, len(replies)-1)]

    @commands.command(pass_context=True, aliases=['8ball'])
    async def meb(self, message):
        """
        8 ball go brrrr
        """
        await message.reply(self.eightball())

    @commands.slash_command(name='8ball', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def meb_slash(self, ctx, question: str):
        await ctx.respond(f" You Asked: `{question}`\n\n{self.eightball()}")


def setup(bot):
    bot.add_cog(EightBall(bot))
