import logging
from random import randrange

from discord.ext import commands

from django.conf import settings

from aadiscordbot import __branch__, __version__

logger = logging.getLogger(__name__)


class Abuse(commands.Cog):
    """
    All about me!
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def respond_to_abuse(self, message):
        replies = [
            "get a dog up ya, cunt",
            "Can I help you? Do you want a time out?",
            "No u",
            "How about Nooooooooo!",
            "Thats a horrible thing to say about your mother",
            "I know you are, but what am I",
            "I'm sorry, did you say something? I don't speak moron",
            "Command accepted! Now commencing with your time out",
            "You kiss your mother with that mouth?!?",
            "Thats what she said"
        ]
        rand = randrange(0, len(replies)-1)
        if message.mention_everyone:
            return
        if self.bot.user.mentioned_in(message):
            await message.reply(replies[rand])


def setup(bot):
    bot.add_cog(Abuse(bot))
