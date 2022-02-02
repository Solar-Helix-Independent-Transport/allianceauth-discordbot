# Cog Stuff
from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color
from ..app_settings import mumble_active, discord_active
# AA Contexts
from aadiscordbot.app_settings import get_site_url, get_admins

from django.conf import settings

import logging
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

    @commands.slash_command(name='auth', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def auth_slash(self, ctx):
        """
        Returns a link to the AllianceAuth Install
        Used by many other Bots and is a common command that users will attempt to run.
        """
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

        return await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Auth(bot))
