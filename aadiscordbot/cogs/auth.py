# Cog Stuff
from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color
# AA Contexts
from aadiscordbot.app_settings import get_site_url
from aadiscordbot.cogs.utils.decorators import sender_is_admin
from allianceauth.services.modules.discord.models import DiscordUser

from aadiscordbot.models import Servers, Channels

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

    @commands.command(pass_context=True)
    @sender_is_admin()
    async def orphans(self, ctx):
        """
        Returns a list of users on this server, who are not known to AA
        """
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
                logger.error(e)
                discord_exists = False
                discord_is_bot = False

            try:
                discord_is_bot = member.bot
            except Exception as e:
                logger.error(e)
                discord_is_bot = False

            if discord_exists is not False:
                # nothing to do, the user exists. Move on with ur life dude.
                pass

            elif discord_is_bot is True:
                # lets also ignore bots here
                pass
            else:
                # Dump the payload if it gets too big
                if len(payload) > 1000:
                    try:
                        await ctx.send(payload)
                        payload = "The following Users cannot be located in Alliance Auth \n"
                    except Exception as e:
                        logger.error(e)
                # keep building the payload
                payload = payload + member.mention + "\n"

        try:
            await ctx.send(payload)
        except Exception as e:
            logger.error(e)

    @commands.command(pass_context=True)
    @sender_is_admin()
    async def populate_models(self, ctx):
        await ctx.channel.trigger_typing()
        await ctx.message.add_reaction(chr(0x231B))

        for guild in list(self.bot.guilds):
            logger.debug(f"Server Name: {guild.name}")
            logger.debug(f"Server ID: {guild.id}")
            Servers.objects.update_or_create(server=guild.id,
                                             defaults={'name': guild.name})
            for channel in list(guild.channels):
                logger.debug(f"Channel Name: {channel.name}")
                logger.debug(f"Channel ID: {channel.id}")
                Channels.objects.update_or_create(channel=channel.id,
                                                  defaults={'server_id': guild.id, 'name': channel.name})


def setup(bot):
    bot.add_cog(Auth(bot))
