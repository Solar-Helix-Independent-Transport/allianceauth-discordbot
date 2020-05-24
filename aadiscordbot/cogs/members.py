import logging
import pendulum
import traceback

import discord

from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color

#log = logging.getLogger(__name__)

from allianceauth.eveonline.models import EveCharacter

from aadiscordbot.cogs.utils.decorators import sender_has_perm

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
        :param ctx:
        :return:
        """
        input_name = ctx.message.content[8:]
        char = EveCharacter.objects.get(character_name=input_name)
        main = char.character_ownership.user.profile.main_character
        state = char.character_ownership.user.profile.state.name
        groups = char.character_ownership.user.groups.all().values_list('name', flat=True)
        try:
            discord = "<@{}>".format(char.character_ownership.user.discord.uid)
        except:
            discord = "unknown"
        alts = char.character_ownership.user.character_ownerships.all().select_related('character', 'zkill').values_list('character__character_name', 'character__corporation_ticker', 'character__character_id', 'character__corporation_id', 'character__zkill__zk_12m', 'character__zkill__zk_3m')
        zk12 = 0
        zk3 = 0
        for alt in alts:
            if alt[4]:
                zk12 += alt[4]
                zk3 += alt[5]

        embed = Embed(title="Character Lookup")
        embed.colour = Color.blue()
        embed.description =  "**{0}** is linked to **{1} [{2}]** ({3})".format(
                                                                        char, 
                                                                        main,
                                                                        main.corporation_ticker,
                                                                        state
                                                                    )

        alt_list = [ "[{}](https://evewho.com/character/{}) *[[{}](https://evewho.com/corporation/{})]*".format(a[0], a[2], a[1], a[3]) for a in alts]
        embed.add_field(
            name="All Linked Characters", value=", ".join(alt_list), inline=False
        )
        embed.add_field(
            name="Groups", value=", ".join(groups), inline=False
        )
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


        await ctx.send(
           
        )



def setup(bot):
    bot.add_cog(Members(bot))
