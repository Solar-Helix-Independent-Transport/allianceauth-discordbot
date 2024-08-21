import logging

from discord.commands import SlashCommandGroup
from discord.ext import commands

from django.core.exceptions import ObjectDoesNotExist

from aadiscordbot.cogs.utils.decorators import sender_is_admin
from aadiscordbot.models import Channels, Servers

logger = logging.getLogger(__name__)


class Models(commands.Cog):
    """
    Django Model Population and Maintenance
    """

    def __init__(self, bot):
        self.bot = bot

    model_commands = SlashCommandGroup(
        "models",
        "Django Model Population",
    )

    @model_commands.command(name="populate")
    @sender_is_admin()
    async def populate_models(self, ctx):
        """
        Populates Django Models for every Channel in the Guild
        """
        await ctx.respond("Populating Models, this might take a while on large servers", ephemeral=True)
        try:
            Servers.objects.update_or_create(
                server=ctx.guild.id,
                defaults={"name": ctx.guild.name}
            )
        except Exception as e:
            logger.error(e)
        server = Servers.objects.get(server=ctx.guild.id)
        for channel in ctx.guild.channels:
            try:
                Channels.objects.update_or_create(
                    channel=channel.id,
                    defaults={
                        "name": channel.name,
                        "server": server
                    }
                )
            except Exception as e:
                logger.error(e)

        return await ctx.respond(f"Django Models Populated for {ctx.guild.name}", ephemeral=True)

    @commands.Cog.listener("on_guild_channel_delete")
    async def on_guild_channel_delete(self, channel):
        try:
            deleted_channel = Channels.objects.get(channel=channel.id)
            deleted_channel.deleted = True
            deleted_channel.save()
        except ObjectDoesNotExist:
            # this is fine
            pass
        except Exception as e:
            logger.error(e)

    @commands.Cog.listener("on_guild_channel_create")
    async def on_guild_channel_create(self, channel):
        try:
            Channels.objects.create(
                channel=channel.id,
                name=channel.name,
                server=Servers.objects.get(server=channel.guild.id)
            )
        except Exception as e:
            logger.error(e)

    @commands.Cog.listener("on_guild_channel_update")
    async def on_guild_channel_update(self, before_channel, after_channel):
        if before_channel.name == after_channel.name:
            pass
        else:
            try:
                Channels.objects.update_or_create(
                    channel=after_channel.id,
                    defaults={"name": after_channel.name}
                )
            except Exception as e:
                logger.error(e)

    @commands.Cog.listener("on_guild_update")
    async def on_guild_update(self, before_guild, after_guild):
        if before_guild.name == after_guild.name:
            pass
        else:
            try:
                Servers.objects.update_or_create(
                    server=after_guild.id,
                    defaults={"name": after_guild.name}
                )
            except Exception as e:
                logger.error(e)


def setup(bot):
    bot.add_cog(Models(bot))
