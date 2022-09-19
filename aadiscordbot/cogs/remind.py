import asyncio
import logging

from discord.ext import commands

from django.conf import settings

logger = logging.getLogger(__name__)


class Remind(commands.Cog):
    """
    Set reminders
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='remind', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def reminder(self, ctx, reminder: str, seconds: int=0, minutes: int=0, hours: int=0, days: int=0):
        counter = 0
        if days:
            counter += days * 60 * 60 * 24
        if hours:
            counter += hours * 60 * 60
        if minutes:
            counter += minutes * 60
        if seconds:
            counter += seconds

        await ctx.send_response(f"Alright, I will remind you about {reminder} in {seconds}s {minutes}m {hours}h {days}d.")
        await asyncio.sleep(seconds)
        await ctx.send_followup(f"{ctx.user.mention} Hi, you asked me to remind you about {reminder}, {seconds}s {minutes}m {hours}h {days}d ago.")

def setup(bot):
    bot.add_cog(Remind(bot))
