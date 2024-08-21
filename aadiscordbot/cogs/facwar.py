import logging

from discord import Embed, option
from discord.ext import commands

from aadiscordbot import app_settings

logger = logging.getLogger(__name__)


class FactionWar(commands.Cog):
    """
    FAction Warfare related helpfull stuffs... Cause moar blues = moar drama....
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='facwar_km', guild_ids=app_settings.get_all_servers())
    @option("esi_link", description="External ESI Killmail link from in game!")
    async def facwar_km(self, ctx, esi_link: str):
        """
            Check an esi killmail link and confirm members were in faction warfare at the time.
        """
        await ctx.defer()
        if not esi_link.startswith("https://esi.evetech.net/"):
            return await ctx.respond("not a valid ESI Killmail link, please try again...")
        km_json = {}
        async with self.bot.session.get(esi_link) as km:
            km_json = await km.json()

        names_to_fetch = set()
        names_to_fetch.add(km_json['victim']['character_id'])
        names_to_fetch.add(km_json['solar_system_id'])
        names_to_fetch.add(km_json['victim']['ship_type_id'])
        names_to_fetch.add(km_json['victim']['character_id'])
        vic_fac = km_json['victim'].get('faction_id', False)
        if vic_fac:
            names_to_fetch.add(km_json['victim'].get('faction_id'))
        for a in km_json['attackers']:
            if a.get('character_id', False):
                names_to_fetch.add(a['character_id'])
                a_fac = a.get('faction_id', False)
                if a_fac:
                    names_to_fetch.add(a.get('faction_id'))
        names = {}
        names_url = "https://esi.evetech.net/latest/universe/names/?datasource=tranquility"
        names_payload = list(names_to_fetch)
        async with self.bot.session.post(names_url, json=names_payload) as nm:
            nms = await nm.json()
            for n in nms:
                names[n['id']] = n['name']

        detail_needed = False or not vic_fac
        e = Embed(title="Kill Report")
        fac_attackers = []
        non_fac_attackers = []
        messages = []

        if vic_fac:
            messages.append(
                f"`{names[km_json['victim']['character_id']]}` was in Faction `{names[km_json['victim'].get('faction_id')]}` when they lost their `{names[km_json['victim']['ship_type_id']]}` in `{names[km_json['solar_system_id']]}`")
        else:
            messages.append(
                f"`{names[km_json['victim']['character_id']]}` was **NOT** in Faction Warfare when they lost their `{names[km_json['victim']['ship_type_id']]}` in `{names[km_json['solar_system_id']]}`")

        for a in km_json['attackers']:
            if a.get('character_id', False):
                a_fac = a.get('faction_id', False)
                if a_fac:
                    fac_attackers.append(
                        f"{names[a['character_id']]} ({names[a['faction_id']]})")
                else:
                    non_fac_attackers.append(f"{names[a['character_id']]}")
                    detail_needed = True

        if len(fac_attackers):
            fac_attack_msg = "\n".join(fac_attackers)
            messages.append("\n**Faction Warfare Attackers**")
            messages.append(f"```\n{fac_attack_msg}\n```")

        if len(non_fac_attackers):
            non_fac_attackers_msg = "\n".join(non_fac_attackers)
            messages.append("\n**Non-Faction Warfare Attackers**")
            messages.append(f"```\n{non_fac_attackers_msg}\n```")

        e.description = "\n".join(messages)

        if detail_needed:
            e.color = 0xe74c3c
        else:
            e.color = 0x2ecc71

        return await ctx.respond(embed=e)


def setup(bot):
    bot.add_cog(FactionWar(bot))
