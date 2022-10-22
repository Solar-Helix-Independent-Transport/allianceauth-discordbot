import logging

from discord import AllowedMentions, Interaction, NotFound
from discord.commands import SlashCommandGroup
from discord.embeds import Embed
from discord.ext import commands
from discord.ui import InputText, Modal

from django.conf import settings
from django.db import IntegrityError

from aadiscordbot.cogs.utils.decorators import sender_has_perm
from aadiscordbot.models import Channels, QuoteMessage, Servers

logger = logging.getLogger(__name__)


class Quote(commands.Cog):
    """
    Save and recall discord messages for quick reference (memes)
    """

    def __init__(self, bot):
        self.bot = bot

    quote_commands = SlashCommandGroup("quote", "Save and Recall Quotes (memes)", guild_ids=[
                                       int(settings.DISCORD_GUILD_ID)])

    class QuoteReference(Modal):
        def __init__(self):
            super().__init__(title="Save Quote")

            self.quote_reference = None

            self.add_item(
                InputText(
                    label="Reference",
                    placeholder="A reference to recall this Quote later, must be unique"
                )
            )

        async def callback(self, interaction: Interaction):
            self.quote_reference = self.children[0].value
            await interaction.response.send_message(f"Attempting to save Quote with reference: {self.quote_reference}", ephemeral=True)
            self.stop()

    @commands.message_command(name="Save Quote", description="Save this message as a Quote", guild_ids=[int(settings.DISCORD_GUILD_ID)])
    @sender_has_perm("aadiscordbot.quote_save")
    async def savequote(self, ctx, message):
        """
        Save a discord message to a Django model for reference later
        """
        ask_for_reference_text = Quote.QuoteReference()
        await ctx.send_modal(ask_for_reference_text)
        await ask_for_reference_text.wait()

        if message.author.nick is None:
            nickname_excepted = message.author.name
        else:
            nickname_excepted = message.author.nick

        try:
            QuoteMessage.objects.update_or_create(
                server_id=message.guild.id,
                channel_id=message.channel.id,
                message=message.id,
                content=message.content,
                datetime=message.created_at,
                author=message.author.id,
                author_nick=(nickname_excepted),
                reference=ask_for_reference_text._children[0].value
            )
            return await message.reply(f"Saved Quote as {ask_for_reference_text._children[0].value}", allowed_mentions=AllowedMentions(replied_user=False))
        except IntegrityError:
            return await ctx.respond(f"Reference is not Unique, Please try again", ephemeral=True)
        except Exception as e:
            return await ctx.respond(e)

    @quote_commands.command(name="recall", description="Recall a Quote from its reference", guild_ids=[int(settings.DISCORD_GUILD_ID)])
    @sender_has_perm("aadiscordbot.quote_recall")
    async def quote_recall(self, ctx, reference: str):
        quote = QuoteMessage.objects.get(reference=reference)
        try:
            await ctx.respond(
                embed=await reconstruct_message(
                    self,
                    ctx,
                    message_id=quote.message
                )
            )
        except Exception as e:
            logger.error(e)

    @commands.user_command(name="View Quotes", description="View a users saved Quotes", guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def recall_user_quotes(self, ctx, user):
        try:
            quotes = QuoteMessage.objects.filter(author=user.id)
        except Exception as e:
            logger.error(e)
        embed = Embed(title=user.name)
        for quote in quotes:
            embed.add_field(
                name=quote.reference,
                value=quote.content,
            )

        return await ctx.respond(embed=embed, ephemeral=True)


async def reconstruct_message(self, ctx, message_id) -> Embed:
    quote = QuoteMessage.objects.get(message=message_id)

    discord_user = ctx.guild.get_member(quote.author)
    if discord_user is None:
        ctx.guild.fetch_member(quote.author)

    discord_channel = ctx.guild.get_channel(quote.channel_id)
    if discord_channel is None:
        try:
            discord_channel = ctx.guild.fetch_channel(quote.channel_id)
            discord_channel_text = discord_channel.mention
        except Exception:
            discord_channel_text = quote.channel.name
    else:
        discord_channel_text = discord_channel.mention

    discord_message = await discord_channel.fetch_message(message_id)

    embed = Embed(title=quote.reference)
    if discord_user is not str:
        embed.set_author(name=discord_user.nick,
                         icon_url=discord_user.avatar.url)
    embed.description = f"> {quote.content}\n\n{discord_channel_text}"
    embed.timestamp = quote.datetime
    if discord_message is not None:
        embed.url = discord_message.jump_url

    return embed


def setup(bot):
    bot.add_cog(Quote(bot))
