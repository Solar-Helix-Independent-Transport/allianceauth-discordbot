"""
"Welcome" cog for discordbot - https://github.com/pvyParts/allianceauth-discordbot
"""
import asyncio
import logging

import discord
from discord.ext import commands

from aadiscordbot.app_settings import get_site_url
from aadiscordbot.models import GoodbyeMessage, WelcomeMessage
from aadiscordbot.utils.auth import user_is_authenticated

logger = logging.getLogger(__name__)


class Welcome(commands.Cog):
    """
    Responds to on_member_join events from discord
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.system_channel
        if channel is not None:
            try:
                # Give AA a chance to save the UID for a joiner.
                await asyncio.sleep(3)
                authenticated = user_is_authenticated(member, member.guild)
            except Exception:
                authenticated = False
            if authenticated:
                try:
                    message = WelcomeMessage.objects.filter(
                        authenticated=True,
                        guild_id=member.guild.id
                    ).order_by('?').first().message
                    message_formatted = message.format(
                        user_mention=member.mention,
                        guild_name=member.guild.name,
                        auth_url=get_site_url(),)
                    await channel.send(message_formatted)
                except IndexError:
                    logger.error(
                        'No Welcome Message configured for Discordbot Welcome cog')
                except Exception as e:
                    logger.error(e)
            else:
                try:
                    message = WelcomeMessage.objects.filter(
                        unauthenticated=True,
                        guild_id=member.guild.id
                    ).order_by('?').first().message
                    message_formatted = message.format(
                        user_mention=member.mention,
                        guild_name=member.guild.name,
                        auth_url=get_site_url(),)
                    await channel.send(message_formatted)
                except IndexError:
                    logger.error(
                        'No Welcome Message configured for Discordbot Welcome cog')
                except Exception as e:
                    logger.error(e)


class Goodbye(commands.Cog):
    """
    Responds to on_member_remove events from discord
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member: discord.Member):
        channel = member.guild.system_channel
        if channel is not None:
            try:
                # Give AA a chance to save the UID for a joiner.
                authenticated = user_is_authenticated(member, member.guild)
            except Exception:
                authenticated = False
            if authenticated:
                # Authenticated
                try:
                    message = GoodbyeMessage.objects.filter(
                        authenticated=True,
                        guild_id=member.guild.id
                    ).order_by('?').first().message
                    message_formatted = message.format(
                        user_mention=member.mention,
                        guild_name=member.guild.name,
                        auth_url=get_site_url(),)
                    await channel.send(message_formatted)
                except IndexError:
                    logger.error(
                        'No Leave Message configured for Discordbot Goodbye cog')
                except Exception as e:
                    logger.error(e)

            else:
                # Un-Authenticated
                try:
                    message = GoodbyeMessage.objects.filter(
                        unauthenticated=True,
                        guild_id=member.guild.id
                    ).order_by('?').first().message
                    message_formatted = message.format(
                        user_mention=member.mention,
                        guild_name=member.guild.name,
                        auth_url=get_site_url(),)
                    await channel.send(message_formatted)
                except IndexError:
                    logger.error(
                        'No Leave Message configured for Discordbot Goodbye cog')
                except Exception as e:
                    logger.error(e)


def setup(bot):
    """
    setup the cog
    :param bot:
    """
    if bot.get_cog("Welcome") is None:
        bot.add_cog(Welcome(bot))

    if bot.get_cog("Goodbye") is None:
        bot.add_cog(Goodbye(bot))
