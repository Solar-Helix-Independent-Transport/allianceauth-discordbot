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

    about_commands = SlashCommandGroup("about", "All about the Bot and Auth", guild_ids=[
                                       int(settings.DISCORD_GUILD_ID)])

    @about_commands.command(name="discordbot", description="About the Discord Bot", guild_ids=[int(settings.DISCORD_GUILD_ID)])
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
        regex = r"^(.+)\/d.+"

        embed.set_footer(
            text="Lovingly developed for Init.™ by AaronRin and ArielKable")

        embed.add_field(
            name="Number of Servers:", value=len(self.bot.guilds), inline=True
        )
        members = 0
        for g in self.bot.guilds:
            members += g.member_count
        embed.add_field(name="Unwilling Monitorees:",
                        value=members, inline=True)
        embed.add_field(
            name="Auth Link", value=f"[{get_site_url()}]({get_site_url()})", inline=False
        )
        embed.add_field(
            name="Version", value=f"{__version__}@{__branch__}", inline=False
        )

        return await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(About(bot))
