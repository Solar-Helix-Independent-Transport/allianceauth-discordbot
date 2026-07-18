"""
"Welcome" cog for discordbot - https://github.com/pvyParts/allianceauth-discordbot
"""
import logging

from discord import Bot, Message, User
from discord.ext import commands

from aadiscordbot.app_settings import get_admins
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
        if type(message.author) is User:
            # Users are DMs or have left
            return

        if message.channel.id in AuthBotConfiguration.get_solo().honeypot_channels.values_list("channel", flat=True):
            author = message.author
            # Caching this here incase it gets lost after the kick
            display_name: str = message.author.display_name
            channel = self.bot.get_channel(message.channel.id)

            if message.author.id in get_admins():
                await channel.send(f"Test Complete <@{author.id}>, you nearly airlocked yourself :sweat_smile:")
                return

            try:
                # Ban the user and delete 5 minutes worth of messages, _on this server_
                # TODO: Consider writing a cross server cleanup task, but this is inbuilt to discord and works.
                await message.author.ban(delete_message_seconds=300, reason="aadiscordbot.cogs.honeypot")
            except Exception as e:
                logger.error(e)
                pass

            try:
                await channel.send(f"Yeet <@{author.id}> `{display_name}`")
            except Exception as e:
                logger.error(e)
                pass

            return
        else:
            return


def setup(bot: Bot) -> None:
    bot.add_cog(Honeypot(bot))
