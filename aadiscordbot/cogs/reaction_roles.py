# Cog Stuff
from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color
from discord.utils import get
# AA Contexts
from django.conf import settings
from aadiscordbot import app_settings
from django.utils import timezone
import pendulum
import re

import logging
import traceback
logger = logging.getLogger(__name__)


class About(commands.Cog):
    """
    All about me!
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def rr(self, ctx):
        """
            Setup the Reaction Role Message
        """
        if ctx.message.author.id not in get_admins():  # https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
            return await ctx.message.add_reaction(chr(0x1F44E))

        await ctx.trigger_typing()

        embed = Embed(title="Group Reaction Roles")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/icons/516758158748811264/ae3991584b0f800b181c936cfc707880.webp?size=128"
        )
        embed.colour = Color.blue()

        embed.description = "Go and add your groups in the admin panel of auth and `!rr` again when you have."
        regex = r"^(.+)\/d.+"
        
        matches = re.finditer(regex, settings.DISCORD_CALLBACK_URL, re.MULTILINE)

        for m in matches:
            url = m.groups()
        embed.set_footer(text=f"Last Updated {timezone.now()}")

        embed.add_field(
            name="Auth Link", value="[{}]({})".format(url[0], url[0]), inline=True
        )

        # embed.add_field(
        #     name="Creator", value="<@318309023478972417>", inline=False
        # )

        return await ctx.send(embed=embed)
