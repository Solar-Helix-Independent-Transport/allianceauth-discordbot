"""
"Welcome" cog for discordbot - https://github.com/pvyParts/allianceauth-discordbot
"""
import io
import logging

from discord import Bot, Message, User, File
from discord.ext import commands

from aadiscordbot.app_settings import get_admins
from aadiscordbot.models import AuthBotConfiguration

logger = logging.getLogger(__name__)


class Honeypot(commands.Cog):
    """
    Monitor a specific channel, Omega-Purge any users that post here.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def omegapurge(self, message: Message) -> None:
        if message.author.bot is True:
            # Easy out, dont catch self or other bots
            return
        if type(message.author) is User:
            # Users are DMs or have left
            return

        if message.channel.id in AuthBotConfiguration.get_solo().honeypot_channels.values_list("channel", flat=True):
            author = message.author
            # Caching this here incase it gets lost after the kick
            display_name: str = message.author.display_name
            channel = self.bot.get_channel(message.channel.id)

            # Preserve the full message content for reporting. Wrap in a code
            # block and escape any triple-backticks in the original message so
            # the report's fence isn't broken (which can result in content
            # appearing missing, e.g. the first line being lost).
            raw_user_message = (
                message.content
                if message.content
                else "No message content, probably just images or embeds…"
            )

            # Format the message creation timestamp as YYYY.MM.DD hh:mm:ss
            created_at_str = message.created_at.strftime("%Y.%m.%d %H:%M:%S")
            report_message = f"## {created_at_str} EVE Time - Honeypot triggered\n"

            if message.author.id in get_admins():
                await channel.send(f"Test Complete <@{author.id}>, you nearly airlocked yourself :sweat_smile:")

                # If a report channel is configured, send a report to it
                if (
                    AuthBotConfiguration.get_solo().honeypot_reports_channel
                    is not None
                ):
                    report_channel = self.bot.get_channel(
                        AuthBotConfiguration.get_solo().honeypot_reports_channel.pk
                    )
                    report_message += (
                        f"User <@{author.id}> `{display_name}` nearly airlocked "
                        "themselves in a honeypot channel on "
                        f"server _{message.guild.name}_, but was saved by their admin status.\n\n"
                        "### Message content"
                    )

                    # Attach the raw message content as a file to avoid any
                    # discord markdown/code-fence parsing issues.
                    try:
                        bio = io.BytesIO(raw_user_message.encode("utf-8"))
                        bio.seek(0)

                        await report_channel.send(
                            content=report_message,
                            file=File(bio, filename="honeypot_message.txt"),
                        )
                    except Exception:
                        logger.exception("Failed to send honeypot report")

                return

            try:
                # Ban the user and delete 5 minutes worth of messages, _on this server_
                # TODO: Consider writing a cross server cleanup task, but this is inbuilt to discord and works.
                await message.author.ban(delete_message_seconds=300, reason="aadiscordbot.cogs.honeypot")

                # If a report channel is configured, send a report to it
                if (
                    AuthBotConfiguration.get_solo().honeypot_reports_channel
                    is not None
                ):
                    report_channel = self.bot.get_channel(
                        AuthBotConfiguration.get_solo().honeypot_reports_channel.pk
                    )
                    report_message += (
                        f"User <@{author.id}> `{display_name}` nearly airlocked "
                        "themselves in a honeypot channel on "
                        f"server _{message.guild.name}_, but was saved by their admin status.\n\n"
                        "### Message content"
                    )

                    # Attach the raw message content as a file to avoid any
                    # discord markdown/code-fence parsing issues.
                    try:
                        bio = io.BytesIO(raw_user_message.encode("utf-8"))
                        bio.seek(0)

                        await report_channel.send(
                            content=report_message,
                            file=File(bio, filename="honeypot_message.txt"),
                        )
                    except Exception:
                        logger.exception("Failed to send honeypot report")
            except Exception as e:
                logger.error(e)
                pass

            try:
                await channel.send(f"Yeet <@{author.id}> `{display_name}`")
            except Exception as e:
                logger.error(e)
                pass

            return
        else:
            return


def setup(bot: Bot) -> None:
    bot.add_cog(Honeypot(bot))
