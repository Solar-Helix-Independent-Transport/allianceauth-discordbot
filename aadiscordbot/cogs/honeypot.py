"""
"Welcome" cog for discordbot - https://github.com/pvyParts/allianceauth-discordbot
"""
import logging

from discord import Bot, Message, User
from discord.ext import commands

from aadiscordbot.models import AuthBotConfiguration

logger = logging.getLogger(__name__)


class Honeypot(commands.Cog):
    """
    Monitor a specific channel, Omega-Purge any users that post here.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def omegapurge(self, message: Message) -> None:
        if message.author.bot is True:
            # Easy out, dont catch self or other bots
            return
        if message.author is User:
            # Users are DMs or have left
            return

        if message.channel.id in AuthBotConfiguration.get_solo().honeypot_channels.values_list("channel"):
            author = message.author
            channel = self.bot.get_channel(message.channel.id)
            try:
                await message.author.ban(delete_message_seconds=300, reason="Honeypot")
            except Exception as e:
                logger.error(e)
                pass

            try:
                channel.send(f"Yeet <@{author.id}>")
            except Exception as e:
                logger.error(e)
                pass
        else:
            return


def setup(bot: Bot) -> None:
    bot.add_cog(Honeypot(bot))
