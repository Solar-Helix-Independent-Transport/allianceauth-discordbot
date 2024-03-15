import logging

from discord.colour import Color
from discord.commands import SlashCommandGroup
from discord.embeds import Embed
from discord.ext import commands

from django.conf import settings

from aadiscordbot import __branch__, __version__
from aadiscordbot.app_settings import get_site_url

logger = logging.getLogger(__name__)


class About(commands.Cog):
    """
    All about me!
    """

    def __init__(self, bot):
        self.bot = bot

    about_commands = SlashCommandGroup("about", "All about the Bot and Auth")

    @about_commands.command(name="discordbot", description="About the Discord Bot")
    async def discordbot(self, ctx):
        """
        All about the bot
        """
        embed = Embed(title="AuthBot: The Authening")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/icons/516758158748811264/ae3991584b0f800b181c936cfc707880.webp?size=128"
        )
        embed.colour = Color.blue()

        embed.description = "This is a multi-de-functional discord bot tailored specifically for Alliance Auth Shenanigans."

        embed.set_footer(
            text="Lovingly developed for Init.™ by AaronRin and ArielKable")

        if not ctx.guild:
            embed.add_field(
                name="Number of Servers:", value=len(self.bot.guilds), inline=True
            )
            members = 0
            for g in self.bot.guilds:
                members += g.member_count
            embed.add_field(name="Unwilling Monitorees:",
                            value=members, inline=True)
            embed.add_field(
                name="Auth Link", value=get_site_url(), inline=False
            )

        embed.add_field(
            name="Version", value=f"{__version__}@{__branch__}", inline=False
        )

        return await ctx.respond(embed=embed)

    @about_commands.command(name="server", description="About this Discord Server")
    async def server(self, ctx):
        """
        All about a server
        """
        if ctx.guild:
            embed = Embed(title=ctx.guild.name)

            if ctx.guild.icon:
                embed.set_thumbnail(
                    url=ctx.guild.icon.url
                )
            embed.color = Color.blue()
            embed.description = "Alliance Auth Managed EvE Online Discord Server!"
            if ctx.guild.description:
                embed.description = ctx.guild.description
            embed.set_footer(
                text="AuthBot Lovingly developed for Init.™ by AaronRin and ArielKable")

            members = ctx.guild.member_count
            embed.add_field(name="Unwilling Monitorees:",
                            value=members, inline=True)

            channels = len(ctx.guild.channels)
            cats = len(ctx.guild.categories)
            embed.add_field(name="Channel Count:",
                            value=channels-cats, inline=True)

            roles = len(ctx.guild.roles)
            embed.add_field(name="Role Count:",
                            value=roles, inline=True)

            embed.add_field(
                name="Auth Link", value=get_site_url(), inline=False
            )

            return await ctx.respond(embed=embed)
        else:
            return await ctx.respond(
                "Sorry, this command cannot be used in DMs."
            )


def setup(bot):
    bot.add_cog(About(bot))
