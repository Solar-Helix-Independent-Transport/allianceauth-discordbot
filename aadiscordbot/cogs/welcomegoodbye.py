"""
"Welcome" cog for discordbot - https://github.com/pvyParts/allianceauth-discordbot
"""

from asyncio import events
from datetime import datetime
from unicodedata import name

from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color
from django.conf import settings

import logging

from aadiscordbot.models import GoodbyeMessage, WelcomeMessage
from aadiscordbot.cogs.utils.decorators import has_perm
from aadiscordbot.app_settings import get_site_url, get_admins
from allianceauth.services.modules.discord.models import DiscordUser

logger = logging.getLogger(__name__)


class Welcome(commands.Cog):
    """
    Responds to on_member_join events from discord
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            try:
                authenticated = DiscordUser.objects.get(uid=member.id).user.has_perm("discord.access_discord")
            except:
                authenticated = False

            if authenticated:
                try:
                    message = WelcomeMessage.objects.filter(authenticated = True).order_by('?')[0].message
                    message_formatted = message.format(
                        user_mention = member.mention,
                        guild_name = member.guild.name,
                        auth_url = get_site_url(),)
                    await channel.send(message_formatted)
                
                except IndexError as e:
                    logger.error('No Welcome Message configured for Discordbot Welcome cog')
                except Exception as e:
                    logger.error(e)
                
            else:
                try:
                    message = WelcomeMessage.objects.filter(authenticated = False).order_by('?')[0].message
                    message_formatted = message.format(
                        user_mention = member.mention,
                        guild_name = member.guild.name,
                        auth_url = get_site_url(),)
                    await channel.send(message_formatted)
                except Exception as e:
                    logger.error(e)
                    
class Goodbye(commands.Cog):
    """
    Responds to on_member_remove events from discord
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            try:
                authenticated = DiscordUser.objects.get(uid=member.id).user.has_perm("discord.access_discord")
            except:
                authenticated = False
            if authenticated:
                # Authenticated
                try:
                    message = GoodbyeMessage.objects.filter(authenticated = True).order_by('?')[0].message
                    message_formatted = message.format(
                        user_mention = member.mention,
                        guild_name = member.guild.name,
                        auth_url = get_site_url(),)
                    await channel.send(message_formatted)
                except IndexError as e:
                    logger.error('No Welcome Message configured for Discordbot Goodbye cog')    
                except Exception as e:
                    logger.error(e)
                
            else:
                # Un-Authenticated
                try:
                    message = GoodbyeMessage.objects.filter(authenticated = False).order_by('?')[0].message
                    message_formatted = message.format(
                        user_mention = member.mention,
                        guild_name = member.guild.name,
                        auth_url = get_site_url(),)
                    await channel.send(message_formatted)
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
