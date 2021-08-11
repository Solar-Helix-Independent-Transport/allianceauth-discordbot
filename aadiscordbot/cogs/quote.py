
# Cog Stuff
from datetime import time
from discord import message
import discord
from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color
from django.conf import settings
# AA Contexts
from aadiscordbot.models import Servers, Channels, Message


import logging

from django.core.exceptions import ObjectDoesNotExist
logger = logging.getLogger(__name__)


class Quote(commands.Cog):
    """
    Save and recall discord messages for quick reference (memes)
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def savequote(self, ctx, quote_ref):
        """
        Save a discord message to a Django model for reference later
        """
        logger.debug("Quote Cog: !savequote received")
        await ctx.channel.trigger_typing()
        await ctx.message.add_reaction(chr(0x231B))

        if ctx.message.reference is not None:
            if ctx.message.reference.cached_message is None:
                # Fetching the message
                channel = self.bot.get_channel(ctx.message.reference.channel_id)
                quoted_message = await channel.fetch_message(ctx.message.reference.message_id)
            else:
                quoted_message = ctx.message.reference.cached_message
        else:
            return await ctx.reply("Please reply to the message you wish to Quote")

        if quoted_message.author.nick is None:
            nickname_excepted = quoted_message.author.name
        else:
            nickname_excepted = quoted_message.author.nick

        Message.objects.create(
            server_id=quoted_message.guild.id,
            channel_id=quoted_message.channel.id,
            message=quoted_message.id,
            content=quoted_message.content,
            datetime=quoted_message.created_at,
            author=quoted_message.author.id,
            author_nick=(nickname_excepted),
            reference=quote_ref
        )

        await ctx.message.clear_reaction(chr(0x231B))

    @commands.command(pass_context=True)
    async def quote(self, ctx, quote_ref):
        """
        Recall a discord message from Django model
        """
        logger.debug("Quote Cog: !quote received")

        await ctx.channel.trigger_typing()
        await ctx.message.add_reaction(chr(0x231B))

        try:
            quote = Message.objects.get(reference=quote_ref)
        except ObjectDoesNotExist:
            return await ctx.reply("Quote not found")

        try:
            discord_user = ctx.bot.get_user(quote.author)
        except:
            discord_user = None

        try:
            discord_channel = await ctx.bot.fetch_channel(quote.channel)
            discord_channel_text = discord_channel.mention
        except:
            discord_channel_text = quote.channel.name

        try:
            discord_message = await ctx.fetch_message(quote.message)
        except:
            discord_message = None


        embed = Embed(title=f"{quote.author_nick}")
        if discord_user is not None:
            embed.set_thumbnail(
                url=discord_user.avatar_url_as(size=32)
            )
            embed.add_field(name="User", value=discord_user.mention)
        embed.description = quote.content
        embed.add_field(name="Time", value=f"<t:{int(quote.datetime.timestamp())}>")
        embed.add_field(name="Channel", value=discord_channel_text)
        if discord_message is not None:
            embed.add_field(name="Link", value=discord_message.jump_url)

        await ctx.message.clear_reaction(chr(0x231B))
        return await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def listquotes(self, ctx):
        """
        Recall a list of valid quotes
        """
        logger.debug("Quote Cog: !listquotes received")

        await ctx.channel.trigger_typing()
        await ctx.message.add_reaction(chr(0x231B))

        quotes = Message.objects.filter(reference__isnull=False).values("reference", "author_nick")

        embed = Embed(title="Quote List")
        
        for quote in quotes:
            embed.add_field(name=quote["reference"], value=quote["author_nick"])

        await ctx.message.clear_reaction(chr(0x231B))   
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Quote(bot))
