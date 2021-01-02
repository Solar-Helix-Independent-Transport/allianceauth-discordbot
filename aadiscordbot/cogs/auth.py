import logging
import pendulum
import traceback
import re

import discord

from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color
from django.conf import settings

from aadiscordbot.app_settings import get_site_url

from allianceauth.services.modules.discord.models import DiscordUser

logger = logging.getLogger(__name__)

class Auth(commands.Cog):
    """
    A Collection of Authentication Tools for Alliance Auth
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def auth(self, ctx):
        """
        Returns a link to the AllianceAuth Install
        Used by many other Bots and is a common command that users will attempt to run.
        """
        await ctx.trigger_typing()

        embed = Embed(title="AllianceAuth")
        embed.set_thumbnail(
            url="https://assets.gitlab-static.net/uploads/-/system/project/avatar/6840712/Alliance_auth.png?width=128"
        )
        embed.colour = Color.blue()

        embed.description = "All Authentication functions for this Discord server are handled through our Alliance Auth install"
        
        url = get_site_url()

        embed.add_field(
            name="Auth Link", value="[{}]({})".format(url, url), inline=False
        )

        return await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def orphans(self, ctx):
        """
        Returns a list of users on this server, who are not known to AA
        """
        if ctx.message.author.id not in app_settings.get_admins(): #https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
            return await ctx.message.delete()

        await ctx.trigger_typing()
        await ctx.send('Searching for Orphaned Discord Users')
        await ctx.trigger_typing()

        payload = "The following Users cannot be located in Alliance Auth \n"

        member_list = ctx.message.guild.members

        for member in member_list:
            id = member.id

            try:
                discord_exists = DiscordUser.objects.get(uid=id)
                discord_is_bot = member.bot
            except Exception as e:
                discord_exists = False
                discord_is_bot = False
            
            try:
                discord_is_bot = member.bot
            except Exception as e:
                discord_is_bot = False

            if discord_exists != False:
                #nothing to do, the user exists. Move on with ur life dude.
                pass

            elif discord_is_bot == True:
                #lets also ignore bots here
                pass
            else:
                payload = payload + member.mention + "\n"

        try:
            await ctx.send(payload)
        except Exception as e:
            await ctx.send(payload[0:1999])
            await ctx.send("Maximum Discord message length reached")


def setup(bot):
    bot.add_cog(Auth(bot))
