import asyncio
from aiohttp import ClientSession

import time
import logging
import pendulum
import traceback
import re
import json
import discord
import aadiscordbot

from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color
from django.conf import settings

#log = logging.getLogger(__name__)

# _stats_request = requests.get("")
# _stats_json = _stats_request.json()
# sleep(1)

#    private static $legacyFlagIDMapping = array(
#        // High Slot => High power slot 1
#        1 => 27,
#        // Medium Slot => Medium power slot 1
#        2 => 19,
#        // Low Slot => Low Power slot 1
#        3 => 11,
#        // Cargo => Cargo
#        4 => 5,
#        // Rig Slot => Rig power slot 1
#        5 => 92,
#        // Drone Bay =>
#        6 => 87,
#        // Sub System => Sub system slot 0
#        7 => 125,
#        // Implant => Implant
#        8 => 89, 
#        // Copy => Cargo, Copy
#        9 => -1
#    );




class Zkill(commands.Cog):
    """
    killboards or something!
    """

    def __init__(self, bot):
        self.bot = bot

    async def fetch_url(self, url, session):
        cached = await self.bot.redis.execute("exists", url)
        if cached:
            return json.loads(await self.bot.redis.execute("get", url))
        async with session.get(url) as response:
            try:
                res = await response.json()
                await self.bot.redis.execute('set', url, json.dumps(res))
                return res
            except:
                return False

    async def bound_fetch(self,sem, url, session):
        # Getter function with semaphore.7
        async with sem:
            return await self.fetch_url(url, session)

    async def lookup_esi_kills(self, kill_id_hashes):
        url = "https://esi.evetech.net/latest/killmails/{}/{}/?datasource=tranquility"

    async def get_zkill_pages(self, ctx):
        url = "https://zkillboard.com/api/allianceID/{}/losses/shipID/{}/"
        esi_url = "https://esi.evetech.net/latest/killmails/{}/{}/?datasource=tranquility"

        tasks = []
        responses = None
        sem = asyncio.Semaphore(100)
        total = len(settings.ALLIANCE_IDS)*len(settings.SHIP_IDS)
        cnt = 1
        async with ClientSession() as session:
            for a in settings.ALLIANCE_IDS:
                for s in settings.SHIP_IDS:
                    await ctx.send(f"Processing Page: {cnt}-{total}")
                    cnt += 1
                    resp = await session.get(url.format(a, s), headers={'Content-Type':'application/json'})
                    try:
                        for km in await resp.json():
                            task = asyncio.ensure_future(self.bound_fetch(sem, 
                                                    esi_url.format(km['killmail_id'], km['zkb']['hash']), session))
                            tasks.append(task)
                    except Exception as e:
                        print(await resp.text())
                        pass
                time.sleep(1)
            responses = await asyncio.gather(*tasks)
            return responses

    @commands.command(pass_context=True)
    async def shitnacks(self, ctx):
        if ctx.message.channel.id not in settings.ADMIN_DISCORD_BOT_CHANNELS:
            return
             
        results = await self.get_zkill_pages(ctx)
        url = "https://zkillboard.com/kill/{}/"
        kills = []
        #print(results)
        for kill in results:
            if kill:
                for i in kill["victim"].get('items',[]):
                    if i['flag'] in settings.SLOT_IDS:
                        if i['item_type_id'] in settings.FLAGGED_IDS:
                            kills.append(url.format(kill['killmail_id']))
        await ctx.send(f"Found {len(kills)} Shitnacks")
        n = 10
        chunks = [list(kills[i * n:(i + 1) * n]) for i in range((len(kills) + n - 1) // n )]

        for c in chunks:
            await ctx.send("\n".join(c))

def setup(bot):
    bot.add_cog(Zkill(bot))