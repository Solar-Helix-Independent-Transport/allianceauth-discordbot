import datetime
import logging

import pendulum
from discord import option
from discord.colour import Color
from discord.commands import SlashCommandGroup
from discord.embeds import Embed
from discord.ext import commands

from django.conf import settings
from django.utils import timezone

from esi.models import Token

from aadiscordbot import app_settings, providers
from aadiscordbot.utils import auth

logger = logging.getLogger(__name__)


class Sov(commands.Cog):
    """
    All about sov!
    """

    def __init__(self, bot):
        self.bot = bot

    sov_commands = SlashCommandGroup(
        "sov",
        "Commands for Managing/Attacking Sov",
        guild_ids=app_settings.get_all_servers()
    )

    def get_search_token(self, uid):
        user = auth.get_auth_user(user=uid)
        tokens = Token.objects.filter(user=user).require_scopes(
            ['esi-search.search_structures.v1'])
        return tokens.first()

    @sov_commands.command(name='lowadm', guild_ids=app_settings.get_all_servers())
    @option(
        "adm",
        float,
        description="Optional ADM Level to flag under.",
        required=False
    )
    async def lowadm(
        self,
        ctx,
        adm
    ):
        """
        Systems with low ADMs.
        """
        if not adm:
            adm = app_settings.get_low_adm()
        #    @commands.command(pass_context=True)
        #    @message_in_channels(settings.SOV_DISCORD_BOT_CHANNELS)

        if ctx.channel.id not in settings.SOV_DISCORD_BOT_CHANNELS:
            return await ctx.respond("You do not have permission to use this command here.", ephemeral=True)

        await ctx.defer()

        own_ids = settings.DISCORD_BOT_SOV_STRUCTURE_OWNER_IDS

        include_regions = settings.DISCORD_BOT_ADM_REGIONS
        include_systems = settings.DISCORD_BOT_ADM_SYSTEMS
        include_constel = settings.DISCORD_BOT_ADM_CONSTELLATIONS

        sov_structures = providers.esi_openapi.client.Sovereignty.GetSovereigntyStructures(
        ).result(
            use_etag=False
        )

        names = {}
        for s in sov_structures:
            if s.alliance_id in own_ids:
                if s.vulnerability_occupancy_level:
                    if s.vulnerability_occupancy_level < adm:
                        names[s.solar_system_id] = {
                            "system_name": s.solar_system_id,
                            "adm": s.vulnerability_occupancy_level
                        }

        if len(names) == 0:
            await ctx.respond(f"All above {adm} :ok_hand:")
            return True

        systems = [k for k, v in names.items()]
        constelations = {}
        for n in systems:
            system = providers.esi_openapi.client.Universe.GetUniverseSystemsSystemId(
                system_id=n
            ).result(
                use_etag=False
            )
            names[n]["system_name"] = system.name
            names[n]["system_id"] = system.system_id
            names[n]["constellation_id"] = system.constellation_id
            if system.constellation_id not in constelations:
                constelations[system.constellation_id] = {}

        for c, v in constelations.items():
            const = providers.esi_openapi.client.Universe.GetUniverseConstellationsConstellationId(
                constellation_id=c
            ).result(
                use_etag=False
            )
            region = providers.esi_openapi.client.Universe.GetUniverseRegionsRegionId(
                region_id=const.region_id
            ).result(
                use_etag=False
            )
            v["region_id"] = const.region_id
            v["region_name"] = region.name
            v["constellation_name"] = const.name

        out_array = {}
        for k, v in names.items():
            out_array[k] = {**v, **constelations[v["constellation_id"]]}

        output = {}
        base_str = "**{}** ADM:{}"
        urls = {}
        for k, h in sorted(out_array.items(), key=lambda e: e[1]['adm']):
            show = False
            if h['region_id'] in include_regions:
                show = True
            elif h['constellation_id'] in include_constel:
                show = True
            elif h['system_id'] in include_systems:
                show = True
            if show:
                if h['region_name'] not in output:
                    output[h['region_name']] = []
                output[h['region_name']].append(
                    base_str.format(
                        h['system_name'],
                        h['adm']
                    )
                )
                if h['region_name'].replace(" ", "_") not in urls:
                    urls[h['region_name'].replace(" ", "_")] = []
                urls[h['region_name'].replace(" ", "_")].append(
                    h['system_name'].replace(" ", "_")
                )
        url = "https://evemaps.dotlan.net/map/{}/{}#adm"

        if len(output) > 0:
            embed = Embed(title="Low ADMs!")
            embed.set_thumbnail(
                url="https://avatars3.githubusercontent.com/u/39349660?s=200&v=4"
            )
            embed.colour = Color.red()
            embed.description = f"Showing systems with ADMs below {adm}. Due to an ESI bug this data might only update once a day at around 2200-2300 Eve Time. **YMMY**\n[For more info please see this issue](https://github.com/esi/esi-issues/issues/1092)"

            await ctx.respond(embed=embed)

            for k, v in output.items():
                n = 25
                chunks = [list(v[i * n:(i + 1) * n])
                          for i in range((len(v) + n - 1) // n)]
                for chunk in chunks:
                    await ctx.send("__{}__\n{}".format(k, "\n".join(chunk)))
            _urls = []
            for r, s in urls.items():
                _urls.append(url.format(r, ",".join(s)))
            await ctx.send("\n\n".join(_urls))
        else:
            await ctx.respond(f"No Systems with ADM below {adm}!")

        return True

    @sov_commands.command(name='vulnerable', guild_ids=app_settings.get_all_servers())
    @option("name_search", str, description="String to search against the sov database.")
    async def vuln(self, ctx, name_search):
        """
        Vulnerable Sov Structures for region/constelation/system/alliance
        """
        if ctx.channel.id not in settings.SOV_DISCORD_BOT_CHANNELS:
            return await ctx.respond("You do not have permission to use this command here.", ephemeral=True)

        await ctx.defer()

        token = self.get_search_token(ctx.author.id)
        if not token:
            return await ctx.respond("No Search token found on auth, please add one", ephemeral=True)
        name_ids = providers.esi_openapi.client.Search.GetCharactersCharacterIdSearch(
            categories=[
                'constellation',
                'solar_system',
                'region',
                'alliance'
            ],
            search=name_search,
            character_id=token.character_id,
            token=token
        ).result(
            use_etag=False
        )

        hit_ids = {
            "a": name_ids.alliance or [],
            "c": name_ids.constellation or [],
            "s": name_ids.solar_system or [],
            "r": name_ids.region or [],
        }

        for r in hit_ids['r']:
            constellations = providers.esi_openapi.client.Universe.GetUniverseRegionsRegionId(
                region_id=r
            ).result(
                use_etag=False
            ).constellations
            for c in constellations:
                if c not in hit_ids["c"]:
                    hit_ids["c"].append(c)

        for c in hit_ids['c']:
            systems = providers.esi_openapi.client.Universe.GetUniverseConstellationsConstellationId(
                constellation_id=c
            ).result(
                use_etag=False
            ).systems
            for s in systems:
                if s not in hit_ids["s"]:
                    hit_ids["s"].append(s)

        sov_structures = providers.esi_openapi.client.Sovereignty.GetSovereigntyStructures(
        ).result(use_etag=False)

        hits = []
        names = []
        alliances = []
        dt_comp = datetime.datetime.utcnow().replace(tzinfo=timezone.utc) + \
            datetime.timedelta(hours=1)

        for s in sov_structures:
            start = s.vulnerable_start_time
            if start:
                if start < dt_comp:
                    if s.solar_system_id in hit_ids["s"] or s.alliance_id in hit_ids["a"]:
                        alliances.append(s.alliance_id)
                        names.append(s.solar_system_id)
                        names.append(s.structure_type_id)
                        hits.append(s)

        if len(names) == 0:
            await ctx.respond(f":sad: Nothing found for '{name_search}'")
            return True

        names_alli = {}
        for a in set(alliances):
            res = providers.esi_openapi.client.Alliance.GetAlliancesAllianceId(
                alliance_id=a
            ).result(
                use_etag=False
            )
            names_alli[a] = res.ticker

        names = providers.esi_openapi.client.Universe.PostUniverseNames(
            body=list(set(names))
        ).result()

        nms = {}
        for n in names:
            nms[n.id] = n.name

        for hit in hits:
            hit.system_name = nms[hit.solar_system_id]
            if hit.structure_type_id == 32226:
                hit.structure = "TCU"
            elif hit.structure_type_id == 32458:
                hit.structure = "IHUB"
            else:
                hit.structure = "¯\\_(ツ)_/¯"

            hit.alliance_name = names_alli[hit.alliance_id]

        output = []
        base_str = "**{}** {} (ADM {})[**{}**] Vulnerable{}"
        dt_now = pendulum.now(tz="UTC")
        for h in sorted(hits, key=lambda k: k['vulnerable_start_time']):
            time = ""
            if h.vulnerable_start_time > dt_now:
                time = " in **{}**".format(pendulum.now(tz="UTC").diff_for_humans(
                    h.vulnerable_start_time, absolute=True
                ))
            else:
                time = " for **{}**".format(pendulum.now(tz="UTC").diff_for_humans(
                    h.vulnerable_end_time, absolute=True
                ))
            output.append(
                base_str.format(
                    h.system_name,
                    h.structure,
                    h.vulnerability_occupancy_level,
                    h.alliance_name,
                    time
                )
            )

        n = 10
        chunks = [list(output[i * n:(i + 1) * n])
                  for i in range((len(output) + n - 1) // n)]
        overflow = ""
        if len(output) > 50:
            overflow = "Only showing first 50..."
        await ctx.respond("Found {} Vunerable Structures for `{}`\n{}\n".format(
            len(output),
            name_search,
            overflow
        ), ephemeral=False
        )

        for c in chunks[:5]:
            await ctx.send("\n".join(c))

    @sov_commands.command(name='search', guild_ids=app_settings.get_all_servers())
    @option("name_search", str, description="String to search against the sov database.")
    async def sov(self, ctx, name_search):
        """
        Sov Details for region/constelation/system/alliance
        """
        if ctx.channel.id not in settings.SOV_DISCORD_BOT_CHANNELS:
            return await ctx.respond("You do not have permission to use this command here.", ephemeral=True)

        await ctx.defer()
        token = self.get_search_token(ctx.author.id)
        if not token:
            return await ctx.respond("No Search token found on auth, please add one", ephemeral=True)
        name_ids = providers.esi_openapi.client.Search.GetCharactersCharacterIdSearch(
            categories=['constellation',
                        'solar_system',
                        'region',
                        'alliance'
                        ],
            search=name_search,
            character_id=token.character_id,
            token=token
        ).result(
            use_etag=False
        )

        hit_ids = {
            "a": name_ids.alliance or [],
            "c": name_ids.constellation or [],
            "s": name_ids.solar_system or [],
            "r": name_ids.region or [],
        }

        for r in hit_ids['r']:
            constellations = providers.esi_openapi.client.Universe.GetUniverseRegionsRegionId(
                region_id=r
            ).result(
                use_etag=False
            ).constellations
            for c in constellations:
                if c not in hit_ids["c"]:
                    hit_ids["c"].append(c)

        for c in hit_ids['c']:
            systems = providers.esi_openapi.client.Universe.GetUniverseConstellationsConstellationId(
                constellation_id=c
            ).result(
                use_etag=False
            ).systems
            for s in systems:
                if s not in hit_ids["s"]:
                    hit_ids["s"].append(s)

        sov_structures = providers.esi_openapi.client.Sovereignty.GetSovereigntyStructures(
        ).result(use_etag=False)

        hits = []
        names = []
        alliances = []

        for s in sov_structures:
            start = s.vulnerable_start_time
            if start:
                if s.solar_system_id in hit_ids["s"] or s.alliance_id in hit_ids["a"]:
                    alliances.append(s.alliance_id)
                    names.append(s.solar_system_id)
                    names.append(s.structure_type_id)
                    hits.append(s)

        if len(names) == 0:
            await ctx.respond(f":sad: Nothing found for '{name_search}'")
            return True

        names_alli = {}
        for a in set(alliances):
            res = providers.esi_openapi.client.Alliance.GetAlliancesAllianceId(
                alliance_id=a
            ).result(
                use_etag=False
            )
            names_alli[a] = res.ticker

        names = providers.esi_openapi.client.Universe.PostUniverseNames(
            body=list(set(names))
        ).result(
            use_etag=False
        )

        nms = {}
        for n in names:
            nms[n.id] = n.name

        for hit in hits:
            hit.system_name = nms[hit.solar_system_id]
            if hit.structure_type_id == 32226:
                hit.structure = "TCU"
            elif hit.structure_type_id == 32458:
                hit.structure = "IHUB"
            else:
                hit.structure = "¯\\_(ツ)_/¯"

            hit.alliance_name = names_alli[hit.alliance_id]

        output = []
        base_str = "**{}** {} (ADM {})[**{}**] Vulnerable{}"
        dt_now = pendulum.now(tz="UTC")
        for h in sorted(hits, key=lambda k: k.vulnerable_start_time):
            time = ""
            time = " for **{}**".format(pendulum.now(tz="UTC").diff_for_humans(
                h.vulnerable_end_time, absolute=True
            ))

            if h.vulnerable_start_time:
                if h.vulnerable_start_time > dt_now:
                    time = " in **{}**".format(pendulum.now(tz="UTC").diff_for_humans(
                        h.vulnerable_start_time, absolute=True
                    ))
            output.append(
                base_str.format(
                    h.system_name,
                    h.structure,
                    h.vulnerability_occupancy_level,
                    h.alliance_name,
                    time
                )
            )

        n = 15
        chunks = [list(output[i * n:(i + 1) * n])
                  for i in range((len(output) + n - 1) // n)]
        overflow = ""
        if len(output) > 50:
            overflow = "Only showing first 50..."

        await ctx.respond("Found {} Sov structures for `{}`\n{}\n".format(
            len(output),
            name_search,
            overflow
        ), ephemeral=False
        )

        for c in chunks[:5]:
            await ctx.send("\n".join(c))


def setup(bot):
    bot.add_cog(Sov(bot))
