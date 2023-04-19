import logging

import pendulum
from aaprom.collectors.discordbot import bot_slash_command
from aaprom.utils import Time, TimeSince
from discord import (
    AutocompleteContext, CategoryChannel, Embed, Role, TextChannel, option,
)
from discord.commands import SlashCommandGroup
from discord.ext import commands

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


class PromExporter(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_application_command")
    async def internal_on_application_command(self, ctx):
        bot_slash_command.labels(command=str(ctx.command), user=str(
            ctx.author), guild=str(ctx.guild)).inc()


def setup(bot):
    bot.add_cog(PromExporter(bot))
