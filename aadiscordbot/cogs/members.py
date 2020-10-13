import logging
import pendulum
import traceback

import discord

from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color

from aadiscordbot.app_settings import authanalitics_active


#log = logging.getLogger(__name__)
from django.conf import settings
from django.contrib.auth.models import User
from allianceauth.eveonline.models import EveCharacter
from allianceauth.eveonline.evelinks import evewho
from aadiscordbot.cogs.utils.decorators import sender_has_perm

from django.core.exceptions import ObjectDoesNotExist

class Members(commands.Cog):
    """
    All about users!
    """

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(pass_context=True)
    @sender_has_perm('corputils.view_alliance_corpstats')
    async def lookup(self, ctx):
        """
        Gets Auth data about a character
        Input: a Eve Character Name
        """
        if ctx.message.channel.id not in settings.ADMIN_DISCORD_BOT_CHANNELS:
            return

        input_name = ctx.message.content[8:]
        char = EveCharacter.objects.get(character_name=input_name)

        try:
            main = char.character_ownership.user.profile.main_character
            state = char.character_ownership.user.profile.state.name
            groups = char.character_ownership.user.groups.all().values_list('name', flat=True)
            
            try:
                discord = "<@{}>".format(char.character_ownership.user.discord.uid)
            except:
                discord = "unknown"

            if authanalitics_active():
                alts = char.character_ownership.user.character_ownerships.all().select_related('character', 'zkil').values_list('character__character_name', 'character__corporation_ticker', 'character__character_id', 'character__corporation_id', 'character__zkill__zk_12m', 'character__zkill__zk_3m')
                zk12 = 0
                zk3 = 0
            else:
                alts = char.character_ownership.user.character_ownerships.all().select_related('character').values_list('character__character_name', 'character__corporation_ticker', 'character__character_id', 'character__corporation_id')
                zk12 = "Not Installed"
                zk3 = "Not Installed" 
            
            if authanalitics_active():
                for alt in alts:
                    if alt[4]:
                        zk12 += alt[4]
                        zk3 += alt[5]

            embed = Embed(title="Character Lookup")
            embed.colour = Color.blue()
            embed.description =  "**{0}** is linked to **{1} [{2}]** (State: {3})".format(
                                                                            char, 
                                                                            main,
                                                                            main.corporation_ticker,
                                                                            state
                                                                        )

            alt_list = [ "[{}](https://evewho.com/character/{}) *[ [{}](https://evewho.com/corporation/{}) ]*".format(a[0], a[2], a[1], a[3]) for a in alts]
            for idx,names in enumerate([alt_list[i:i + 6] for i in range(0, len(alt_list), 6)]):
                if idx < 6:
                    embed.add_field(
                        name="Linked Characters {}".format(idx+1), value=", ".join(names), inline=False
                    )
                else:
                    embed.add_field(
                        name="Linked Characters {} **( Discord Limited There are More )**".format(idx), value=", ".join(names), inline=False
                    )
                    break


            if len(groups)>0:
                embed.add_field(
                    name="Groups", value=", ".join(groups), inline=False
                )
                
            if authanalitics_active():
                embed.add_field(
                    name="12m Kills", value=zk12, inline=True
                )
                embed.add_field(
                    name="3m Kills", value=zk3, inline=True
                )

            embed.add_field(
                name="Discord Link", value=discord, inline=False
            )

            return await ctx.send(embed=embed)
        except ObjectDoesNotExist:
            users = char.ownership_records.values('user')
            users = User.objects.filter(id__in=users)
            characters = EveCharacter.objects.filter(ownership_records__user__in=users).distinct()
            embed = Embed(title="Character Lookup")
            embed.colour = Color.blue()

            embed.description =  "**{0}** is Unlinked searching for any characters linked to known users".format(
                                                                char, 
                                                            )
            user_names = [ "{}".format(user.username) for user in users ]
            embed.add_field(
                name="Old Users", value=", ".join(user_names), inline=False
            )
            alt_list = [ "[{}](https://evewho.com/character/{}) *[ [{}](https://evewho.com/corporation/{}) ]*".format(a.character_name,
                                                                                                                     a.character_id, 
                                                                                                                     a.corporation_ticker, 
                                                                                                                     a.corporation_id
                                                                                                                     ) for a in characters]
            for idx,names in enumerate([alt_list[i:i + 6] for i in range(0, len(alt_list), 6)]):
                if idx < 6:
                    embed.add_field(
                        name="Found Characters {}".format(idx+1), value=", ".join(names), inline=False
                    )
                else:
                    embed.add_field(
                        name="Found Characters {} **( Discord Limited There are More )**".format(idx), value=", ".join(names), inline=False
                    )
                    break

            return await ctx.send(embed=embed)

    @commands.command(pass_context=True)    
    @sender_has_perm('corputils.view_alliance_corpstats')
    async def altcorp(self, ctx):
        """
        Gets Auth data about an altcorp
        Input: a Eve Character Name
        """
        if ctx.message.channel.id not in settings.ADMIN_DISCORD_BOT_CHANNELS:
            return

        input_name = ctx.message.content[9:]
        chars = EveCharacter.objects.filter(corporation_name=input_name)
        own_ids = [settings.DISCORD_BOT_MEMBER_ALLIANCES]
        alts_in_corp = []
        for c in chars:
            if c.alliance_id not in own_ids:
                alts_in_corp.append(c)

        mains = {}
        for a in alts_in_corp:
            try:
                main = a.character_ownership.user.profile.main_character
                if main.character_id not in mains:
                    mains[main.character_id] = [main,0]
                mains[main.character_id][1]+=1
                alt_corp_id = a.corporation_id
            except:
                pass
        output = []
        base_string = "[{}]({}) [ [{}]({}) ] has {} alt{}"
        for k,m in mains.items():
            output.append(
                base_string.format(
                    m[0],
                    evewho.character_url(m[0].character_id),
                    m[0].corporation_ticker,
                    evewho.corporation_url(m[0].corporation_id),
                    m[1],
                    "s" if m[1]>1 else ""
                )
            )

        for strings in [output[i:i + 10] for i in range(0, len(output), 10)]:  
            embed = Embed(title=input_name)
            embed.colour = Color.blue()
            embed.description = "\n".join(strings)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Members(bot))
