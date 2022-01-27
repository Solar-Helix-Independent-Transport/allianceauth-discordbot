# Cog Stuff
from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color
# AA Contexts
from django.conf import settings
from allianceauth.eveonline.models import EveCharacter
from aadiscordbot.cogs.utils.decorators import sender_has_perm
from aadiscordbot import app_settings, providers

import datetime
from django.utils import timezone

import pendulum
import logging
logger = logging.getLogger(__name__)

class Sov(commands.Cog):
    """
    All about sov!
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @message_in_channels(settings.SOV_DISCORD_BOT_CHANNELS)
    async def vuln(self, ctx):
        """
        Timers for region/constelation/system/alliance
        """
        await ctx.trigger_typing()

        name_search = ctx.message.content[6:]

        name_ids = providers.esi.client.Search.get_search(
            categories=['constellation',
                        'solar_system',
                        'region',
                        'alliance'
                        ],
            search=name_search
        ).result()

        hit_ids = {
            "a": name_ids.get("alliance") or [],
            "c": name_ids.get("constellation") or [],
            "s": name_ids.get("solar_system") or [],
            "r": name_ids.get("region") or [],
        }

        for r in hit_ids['r']:
            constellations = providers.esi.client.Universe.get_universe_regions_region_id(region_id=r).result()["constellations"]
            for c in constellations:
                if c not in hit_ids["c"]:
                    hit_ids["c"].append(c)

        for c in hit_ids['c']:
            systems = providers.esi.client.Universe.get_universe_constellations_constellation_id(constellation_id=c).result()["systems"]
            for s in systems:
                if s not in hit_ids["s"]:
                    hit_ids["s"].append(s)

        sov_structures = providers.esi.client.Sovereignty.get_sovereignty_structures().result()

        hits = []
        names = []
        alliances = []
        dt_comp = datetime.datetime.utcnow().replace(tzinfo=timezone.utc) + datetime.timedelta(hours=1)

        for s in sov_structures:
            start = s.get('vulnerable_start_time', False)
            if start:
                if start < dt_comp:
                    if s.get('solar_system_id') in hit_ids["s"] or s.get('alliance_id') in hit_ids["a"]:
                        alliances.append(s.get('alliance_id'))
                        names.append(s.get('solar_system_id'))
                        names.append(s.get('structure_type_id'))
                        hits.append(s)

        if len(names) == 0:
            await ctx.send(":sad: Nothing found for '{}'".format(name_search))
            return True

        names_alli = {}
        for a in set(alliances):
            res = providers.esi.client.Alliance.get_alliances_alliance_id(alliance_id=a).result()
            names_alli[a] = res.get("ticker")

        names = providers.esi.client.Universe.post_universe_names(ids=list(set(names))).result()

        nms = {}
        for n in names:
            nms[n.get("id")] = n.get("name")

        for hit in hits:
            hit['system_name'] = nms[hit.get('solar_system_id')]
            if hit.get("structure_type_id") == 32226:
                hit['structure'] = "TCU"
            elif hit.get("structure_type_id") == 32458:
                hit['structure'] = "IHUB"
            else:
                hit['structure'] = "¯\\_(ツ)_/¯"

            hit['alliance_name'] = names_alli[hit.get('alliance_id')]

        output = []
        base_str = "**{}** {} (ADM {})[**{}**] Vulnerable{}"
        dt_now = pendulum.now(tz="UTC")
        for h in sorted(hits, key=lambda k: k['vulnerable_start_time']):
            time = ""
            if h['vulnerable_start_time'] > dt_now:
                time = " in **{}**".format(pendulum.now(tz="UTC").diff_for_humans(
                            h['vulnerable_start_time'], absolute=True
                        ))
            else:
                time = " for **{}**".format(pendulum.now(tz="UTC").diff_for_humans(
                            h['vulnerable_end_time'], absolute=True
                        ))
            output.append(
                base_str.format(
                    h['system_name'],
                    h['structure'],
                    h['vulnerability_occupancy_level'],
                    h['alliance_name'],
                    time
                )
            )

        n = 10
        chunks = [list(output[i * n:(i + 1) * n]) for i in range((len(output) + n - 1) // n)]

        for c in chunks:
            await ctx.send("\n".join(c))
        return True

    @commands.command(pass_context=True)
    @message_in_channels(settings.SOV_DISCORD_BOT_CHANNELS)
    async def sov(self, ctx):
        """
        Timers for region/constelation/system/alliance
        """
        await ctx.trigger_typing()

        name_search = ctx.message.content[5:]

        name_ids = providers.esi.client.Search.get_search(
            categories=['constellation',
                        'solar_system',
                        'region',
                        'alliance'
                        ],
            search=name_search
        ).result()

        hit_ids = {
            "a": name_ids.get("alliance") or [],
            "c": name_ids.get("constellation") or [],
            "s": name_ids.get("solar_system") or [],
            "r": name_ids.get("region") or [],
        }

        for r in hit_ids['r']:
            constellations = providers.esi.client.Universe.get_universe_regions_region_id(region_id=r).result()["constellations"]
            for c in constellations:
                if c not in hit_ids["c"]:
                    hit_ids["c"].append(c)

        for c in hit_ids['c']:
            systems = providers.esi.client.Universe.get_universe_constellations_constellation_id(constellation_id=c).result()["systems"]
            for s in systems:
                if s not in hit_ids["s"]:
                    hit_ids["s"].append(s)

        sov_structures = providers.esi.client.Sovereignty.get_sovereignty_structures().result()

        hits = []
        names = []
        alliances = []

        for s in sov_structures:
            start = s.get('vulnerable_start_time', False)
            if start:
                if s.get('solar_system_id') in hit_ids["s"] or s.get('alliance_id') in hit_ids["a"]:
                    alliances.append(s.get('alliance_id'))
                    names.append(s.get('solar_system_id'))
                    names.append(s.get('structure_type_id'))
                    hits.append(s)

        if len(names) == 0:
            await ctx.send(":sad: Nothing found for '{}'".format(name_search))
            return True

        names_alli = {}
        for a in set(alliances):
            res = providers.esi.client.Alliance.get_alliances_alliance_id(alliance_id=a).result()
            names_alli[a] = res.get("ticker")

        names = providers.esi.client.Universe.post_universe_names(ids=list(set(names))).result()

        nms = {}
        for n in names:
            nms[n.get("id")] = n.get("name")

        for hit in hits:
            hit['system_name'] = nms[hit.get('solar_system_id')]
            if hit.get("structure_type_id") == 32226:
                hit['structure'] = "TCU"
            elif hit.get("structure_type_id") == 32458:
                hit['structure'] = "IHUB"
            else:
                hit['structure'] = "¯\\_(ツ)_/¯"

            hit['alliance_name'] = names_alli[hit.get('alliance_id')]

        output = []
        base_str = "**{}** {} (ADM {})[**{}**] Vulnerable{}"
        dt_now = pendulum.now(tz="UTC")
        for h in sorted(hits, key=lambda k: k['vulnerable_start_time']):
            time = ""
            time = " for **{}**".format(pendulum.now(tz="UTC").diff_for_humans(
                h['vulnerable_end_time'], absolute=True
            ))

            if h['vulnerable_start_time']:
                if h['vulnerable_start_time'] > dt_now:
                    time = " in **{}**".format(pendulum.now(tz="UTC").diff_for_humans(
                                h['vulnerable_start_time'], absolute=True
                            ))
            output.append(
                base_str.format(
                    h['system_name'],
                    h['structure'],
                    h['vulnerability_occupancy_level'],
                    h['alliance_name'],
                    time
                )
            )

        n = 15
        chunks = [list(output[i * n:(i + 1) * n]) for i in range((len(output) + n - 1) // n)]

        for c in chunks:
            await ctx.send("\n".join(c))
        return True

    @commands.command(pass_context=True)
    @message_in_channels(settings.SOV_DISCORD_BOT_CHANNELS)
    async def lowadm(self, ctx):
        """
        Timers for region/constelation/system/alliance
        """
        await ctx.trigger_typing()

        own_ids = settings.DISCORD_BOT_SOV_STRUCTURE_OWNER_IDS

        include_regions = settings.DISCORD_BOT_ADM_REGIONS
        include_systems = settings.DISCORD_BOT_ADM_SYSTEMS
        include_constel = settings.DISCORD_BOT_ADM_CONSTELLATIONS

        sov_structures = providers.esi.client.Sovereignty.get_sovereignty_structures().result()

        names = {}
        alliances = []
        for s in sov_structures:
            if s.get('alliance_id') in own_ids:
                if s.get('vulnerability_occupancy_level'):
                    if s.get('vulnerability_occupancy_level') < app_settings.get_low_adm():
                        names[s.get('solar_system_id')] = {
                            "system_name": s.get('solar_system_id'),
                            "adm": s.get('vulnerability_occupancy_level')
                        }

        if len(names) == 0:
            await ctx.send("All above 5! :ok_hand:")
            return True

        systems = [k for k, v in names.items()]
        constelations = {}
        region_id = {}
        for n in systems:
            system = providers.esi.client.Universe.get_universe_systems_system_id(system_id=n).result()
            names[n]["system_name"] = system.get("name")
            names[n]["system_id"] = system.get("system_id")
            names[n]["constellation_id"] = system.get("constellation_id")
            if system.get("constellation_id") not in constelations:
                constelations[system.get("constellation_id")] = {}

        for c, v in constelations.items():
            const = providers.esi.client.Universe.get_universe_constellations_constellation_id(constellation_id=c).result()
            region = providers.esi.client.Universe.get_universe_regions_region_id(region_id=const.get("region_id")).result()
            v["region_id"] = const.get("region_id")
            v["region_name"] = region.get("name")
            v["constellation_name"] = const.get("name")

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
            for k, v in output.items():
                n = 25
                chunks = [list(v[i * n:(i + 1) * n]) for i in range((len(v) + n - 1) // n)]
                for chunk in chunks:
                    await ctx.send("__{}__\n{}".format(k, "\n".join(chunk)))
            await ctx.send(url.format(k.replace(" ", "_"), ",".join(urls[k.replace(" ", "_")])))

        else:
            await ctx.send(f"No Systems with ADM below {app_settings.get_low_adm()}")

        embed = Embed(title="Disclaimer")
        embed.set_thumbnail(
            url="https://avatars3.githubusercontent.com/u/39349660?s=200&v=4"
        )
        embed.colour = Color.red()
        embed.description = "Due to an ESI bug this data might only update once a day at around 2200-2300 Eve Time. **YMMY**\n[For more info please see this issue](https://github.com/esi/esi-issues/issues/1092)"
        await ctx.send(embed=embed)

        return True


def setup(bot):
    bot.add_cog(Sov(bot))
