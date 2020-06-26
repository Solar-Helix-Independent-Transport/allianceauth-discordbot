import logging
import pendulum
import traceback

import discord

from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color

#log = logging.getLogger(__name__)

from django.conf import settings
from allianceauth.eveonline.models import EveCharacter
from aadiscordbot.cogs.utils.decorators import sender_has_perm
from .. import providers

import datetime
from django.utils import timezone

class Sov(commands.Cog):
    """
    All about sov!
    """

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(pass_context=True)
    async def vuln(self, ctx):
        """
        Timers for region/constelation/system/alliance
        """
        if ctx.message.channel.id not in settings.SOV_DISCORD_BOT_CHANNELS:
            return False

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
                    if  s.get('solar_system_id') in hit_ids["s"] or s.get('alliance_id') in hit_ids["a"]:
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
                hit['structure'] = "¯\_(ツ)_/¯"

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
        chunks = [list(output[i * n:(i + 1) * n]) for i in range((len(output) + n - 1) // n )]

        for c in chunks:
            await ctx.send("\n".join(c))
        return True


def setup(bot):
    bot.add_cog(Sov(bot))
