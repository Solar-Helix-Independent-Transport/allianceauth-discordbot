# Cog Stuff
import discord
from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color
from discord.utils import get
from random import randrange
# AA Contexts
from django.conf import settings
from aadiscordbot.cogs.utils.decorators import sender_is_admin
from aadiscordbot import app_settings, __version__, __branch__

import pendulum
import re

import hashlib
import logging

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


def setup(bot):
    bot.add_cog(Abuse(bot))
