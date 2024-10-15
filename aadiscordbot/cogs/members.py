import logging

from discord import AutocompleteContext
from discord.colour import Color
from discord.commands import option
from discord.embeds import Embed
from discord.ext import commands

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from allianceauth.eveonline.evelinks import evewho
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo

from aadiscordbot.app_settings import aastatistics_active
from aadiscordbot.cogs.utils.autocompletes import search_characters
from aadiscordbot.cogs.utils.decorators import (
    is_guild_managed, message_in_channels, sender_has_any_perm,
)

logger = logging.getLogger(__name__)


class Members(commands.Cog):
    """
    All about users!
    """

    def __init__(self, bot):
        self.bot = bot

    def get_lookup_embed(self, input_name):
        embed = Embed(
            title="Character Lookup {character_name}".format(
                character_name=input_name)
        )

        try:
            char = EveCharacter.objects.get(character_name=input_name)

            try:
                main = char.character_ownership.user.profile.main_character
                state = char.character_ownership.user.profile.state.name
                groups = char.character_ownership.user.groups.all().values_list('name', flat=True)

                try:
                    discord_string = "<@{}>".format(
                        char.character_ownership.user.discord.uid)
                except Exception as e:
                    logger.error(e)
                    discord_string = "unknown"

                if aastatistics_active():
                    alts = char.character_ownership.user.character_ownerships.all().select_related('character', 'character_stats').values_list('character__character_name',
                                                                                                                                               'character__corporation_ticker', 'character__character_id', 'character__corporation_id', 'character__character_stats__zk_12m', 'character__character_stats__zk_3m')
                    zk12 = 0
                    zk3 = 0
                else:
                    alts = char.character_ownership.user.character_ownerships.all().select_related('character').values_list(
                        'character__character_name', 'character__corporation_ticker', 'character__character_id', 'character__corporation_id')
                    zk12 = "Not Installed"
                    zk3 = "Not Installed"

                if aastatistics_active():
                    for alt in alts:
                        if alt[4]:
                            zk12 += alt[4]
                            zk3 += alt[5]

                embed.colour = Color.blue()
                embed.description = "**{}** is linked to **{} [{}]** (State: {})".format(
                    char,
                    main,
                    main.corporation_ticker,
                    state
                )

                alt_list = ["[{}](https://evewho.com/character/{}) *[ [{}](https://evewho.com/corporation/{}) ]*".format(
                    a[0], a[2], a[1], a[3]) for a in alts]
                for idx, names in enumerate([alt_list[i:i + 6] for i in range(0, len(alt_list), 6)]):
                    if idx < 6:
                        embed.add_field(
                            name=f"Linked Characters {idx + 1}", value=", ".join(names), inline=False
                        )
                    else:
                        embed.add_field(
                            name=f"Linked Characters {idx} **( Discord Limited There are More )**", value=", ".join(names), inline=False
                        )
                        break

                if len(groups) > 0:
                    embed.add_field(
                        name="Groups", value=", ".join(groups), inline=False
                    )

                if aastatistics_active():
                    embed.add_field(
                        name="12m Kills", value=zk12, inline=True
                    )
                    embed.add_field(
                        name="3m Kills", value=zk3, inline=True
                    )

                embed.add_field(
                    name="Discord Link", value=discord_string, inline=False
                )

                return embed
            except ObjectDoesNotExist:
                users = char.ownership_records.values('user')
                users = User.objects.filter(id__in=users)
                characters = EveCharacter.objects.filter(
                    ownership_records__user__in=users).distinct()
                embed = Embed(title="Character Lookup")
                embed.colour = Color.blue()

                embed.description = "**{}** is Unlinked searching for any characters linked to known users".format(
                    char,
                )
                user_names = [f"{user.username}" for user in users]
                if len(user_names) == 0:
                    user_names = "No User Links found"
                else:
                    user_names = ", ".join(user_names)

                embed.add_field(
                    name="Old Users", value=user_names, inline=False
                )

                alt_list = ["[{}](https://evewho.com/character/{}) *[ [{}](https://evewho.com/corporation/{}) ]*".format(a.character_name,
                                                                                                                         a.character_id,
                                                                                                                         a.corporation_ticker,
                                                                                                                         a.corporation_id
                                                                                                                         ) for a in characters]
                for idx, names in enumerate([alt_list[i:i + 6] for i in range(0, len(alt_list), 6)]):
                    if idx < 6:
                        embed.add_field(
                            name=f"Found Characters {idx + 1}", value=", ".join(names), inline=False
                        )
                    else:
                        embed.add_field(
                            name=f"Found Characters {idx} **( Discord Limited There are More )**", value=", ".join(names), inline=False
                        )
                        break

                return embed

        except EveCharacter.DoesNotExist:
            embed.colour = Color.red()

            embed.description = (
                "Character **{character_name}** does not exist in our Auth system"
            ).format(character_name=input_name)

            return embed

    @commands.command(pass_context=True)
    @is_guild_managed()
    @sender_has_any_perm(['corputils.view_alliance_corpstats', 'corpstats.view_alliance_corpstats', 'aadiscordbot.member_command_access'])
    @message_in_channels(settings.ADMIN_DISCORD_BOT_CHANNELS)
    async def lookup(self, ctx):
        """
        Gets Auth data about a character
        Input: a Eve Character Name
        """
        input_name = ctx.message.content[8:]
        return await ctx.send(embed=self.get_lookup_embed(input_name))

    @commands.slash_command(name='lookup')
    @is_guild_managed()
    @sender_has_any_perm(['corputils.view_alliance_corpstats', 'corpstats.view_alliance_corpstats', 'aadiscordbot.member_command_access'])
    @message_in_channels(settings.ADMIN_DISCORD_BOT_CHANNELS)
    @option("character", description="Search for a Character!", autocomplete=search_characters)
    async def slash_lookup(
        self,
        ctx,
        character: str,
    ):
        await ctx.defer()
        return await ctx.respond(embed=self.get_lookup_embed(character))

    async def search_corps_on_characters(ctx: AutocompleteContext):
        """Returns a list of corporations that begin with the characters entered so far."""
        return list(EveCharacter.objects.filter(corporation_name__icontains=ctx.value).values_list('corporation_name', flat=True).distinct()[:10])

    def build_altcorp_embeds(self, input_name):
        chars = EveCharacter.objects.filter(corporation_name=input_name)
        if chars.count():
            corp_id = 0
            own_ids = [settings.DISCORD_BOT_MEMBER_ALLIANCES]
            alts_in_corp = []
            knowns = 0
            for c in chars:
                corp_id = c.corporation_id
                if c.alliance_id not in own_ids:
                    alts_in_corp.append(c)

            mains = {}
            for a in alts_in_corp:
                try:
                    main = a.character_ownership.user.profile.main_character
                    if main.character_id not in mains:
                        mains[main.character_id] = [main, 0]
                    mains[main.character_id][1] += 1
                    knowns += 1
                except Exception:
                    # logger.error(e)
                    pass
            output = []
            base_string = "[{}]({}) [ [{}]({}) ] has {} alt{}"
            for k, m in mains.items():
                output.append(
                    base_string.format(
                        m[0],
                        evewho.character_url(m[0].character_id),
                        m[0].corporation_ticker,
                        evewho.corporation_url(m[0].corporation_id),
                        m[1],
                        "s" if m[1] > 1 else ""
                    )
                )
            embeds = []

            corp_info = EveCorporationInfo.provider.get_corporation(corp_id)

            msg = f"**[ [{corp_info.ticker}]({evewho.corporation_url(corp_id)}) ]** has {corp_info.members} members:\n\n"\
                f"```diff\n"\
                f"+Known Members     : {knowns}\n"\
                f"-Unknowns          : {corp_info.members - knowns}```"

            _header = Embed(
                title=input_name,
                description=msg
            )

            embeds.append(_header)

            for strings in [output[i:i + 10] for i in range(0, len(output), 10)]:
                embed = Embed(title=input_name)
                embed.colour = Color.blue()
                embed.description = "\n".join(strings)
                embeds.append(embed)
            return embeds

    @commands.slash_command(name='altcorp')
    @is_guild_managed()
    @sender_has_any_perm(['aadiscordbot.member_command_access'])
    @message_in_channels(settings.ADMIN_DISCORD_BOT_CHANNELS)
    @option("corporation",
            description="Search for a Character!",
            autocomplete=search_corps_on_characters)
    async def slash_altcorp(
        self,
        ctx,
        corporation: str,
    ):
        await ctx.defer()
        embeds = self.build_altcorp_embeds(corporation)
        if len(embeds):
            e = embeds.pop(0)
            await ctx.respond(embed=e)
            for e in embeds:
                await ctx.send(embed=e)
        else:
            await ctx.respond("No Members Found!")

    @commands.command(pass_context=True)
    @is_guild_managed()
    @sender_has_any_perm(['aadiscordbot.member_command_access'])
    @message_in_channels(settings.ADMIN_DISCORD_BOT_CHANNELS)
    async def altcorp(self, ctx):
        """
        Gets Auth data about an altcorp
        Input: a Eve Character Name
        """
        corporation = ctx.message.content[9:]
        embeds = self.build_altcorp_embeds(corporation)
        if len(embeds):
            for e in embeds:
                await ctx.send(embed=e)
        else:
            await ctx.send("No Members Found!")


def setup(bot):
    bot.add_cog(Members(bot))
