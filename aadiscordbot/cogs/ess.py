import logging

from discord import AutocompleteContext, Embed, option
from discord.ext import commands
from discord.utils import get

from django.conf import settings

from ..app_settings import DISCORD_BOT_ESS_PING_CHANNEL_ID

logger = logging.getLogger(__name__)


class EssLinks(commands.Cog):
    """
    All about ESS Links
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='ess', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    @option("system", description="What System has been linked?")
    @option("isk", required=False, description="What is the value of the reserve bank?")
    @option("key_type", required=False, description="15min or 45min?")
    @option("message", required=False, description="anything else to add?")
    async def ess_slash(self, ctx, system: str, isk: int, key_type: str, message: str):
        """
            Ping the FC Team for ESS Saves
        """
        msg = []
        extra_message = ""
        if isk:
            msg.append(f"Reported Value in ESS Bank: `${isk:,}`")
        if key_type:
            msg.append(f"Reported Key Type: `{key_type}`")
        if message:
            msg.append(f"Notes: {message}")
        if len(msg):
            extra_message = "\n".join(msg)
        e = Embed(title="ESS Event Reported!",
                  description=f"System: `{system}`\n{extra_message}\nReported by <@{ctx.author.id}>", color=0x992d22)

        chn = get(ctx.guild.channels, id=DISCORD_BOT_ESS_PING_CHANNEL_ID)

        await chn.send("@here", embed=e)
        await ctx.respond("Successfully Pinged the FC's, They will be in touch if they need to be.", ephemeral=True)


def setup(bot):
    bot.add_cog(EssLinks(bot))
