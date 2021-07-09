"""
Market Price Checks
"""

import requests

# Cog Stuff
from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color


import logging
logger = logging.getLogger(__name__)


class PriceCheck(commands.Cog):
    """
    price checks on Jita and Amarr markets
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def price(self, ctx):
        """
        Check an item price on Jita and Amarr market
        :param ctx:
        :return:
        """

        markets = [
            {"name": "Jita", "api_key": "jita"},
            {"name": "Amarr", "api_key": "amarr"},
        ]

        await ctx.trigger_typing()

        item_name = ctx.message.content[7:]

        await self.price_check(ctx=ctx, markets=markets, item_name=item_name)

    @commands.command(pass_context=True)
    async def jita(self, ctx):
        """
        Check an item price on Jita market
        :param ctx:
        :return:
        """

        markets = [
            {"name": "Jita", "api_key": "jita"},
        ]

        await ctx.trigger_typing()

        item_name = ctx.message.content[6:]

        await self.price_check(ctx=ctx, markets=markets, item_name=item_name)

    @commands.command(pass_context=True)
    async def amarr(self, ctx):
        """
        Check an item price on Amarr market
        :param ctx:
        :return:
        """

        markets = [
            {"name": "Amarr", "api_key": "amarr"},
        ]

        await ctx.trigger_typing()

        item_name = ctx.message.content[7:]

        await self.price_check(ctx=ctx, markets=markets, item_name=item_name)

    async def price_check(self, ctx, markets, item_name: str = None):
        """
        do the price checks and post to Discord
        :param ctx:
        :param markets:
        :param item_name:
        :return:
        """

        has_thumbnail = False

        await ctx.trigger_typing()

        if item_name != "":
            embed = Embed(
                title="Price Lookup for {item_name}".format(item_name=item_name),
                color=Color.green(),
            )

            for market in markets:
                embed.add_field(
                    name="{market_name} Market".format(market_name=market["name"]),
                    value="Prices for {item_name} on the {market_name} Market.".format(
                        item_name=item_name, market_name=market["name"]
                    ),
                    inline=False,
                )

                market_data = requests.post(
                    "https://evepraisal.com/appraisal/structured.json",
                    json={
                        "market_name": market["api_key"],
                        "items": [{"name": item_name}],
                    },
                )

                if market_data.status_code == 200:
                    market_json = market_data.json()

                    if has_thumbnail is False:
                        embed.set_thumbnail(
                            url=(
                                "https://images.evetech.net/types/{type_id}/icon?size=64"
                            ).format(
                                type_id=market_json["appraisal"]["items"][0]["typeID"]
                            )
                        )

                        has_thumbnail = True

                    # sell order price
                    market_sell_order_price = f'{market_json["appraisal"]["items"][0]["prices"]["sell"]["min"]:,} ISK'  # noqa: E501

                    if (
                        market_json["appraisal"]["items"][0]["prices"]["sell"][
                            "order_count"
                        ]
                        == 0
                    ):
                        market_sell_order_price = "No sell orders found"

                    embed.add_field(
                        name="Sell Order Price",
                        value=market_sell_order_price,
                        inline=True,
                    )

                    # buy order price
                    market_buy_order_price = f'{market_json["appraisal"]["items"][0]["prices"]["buy"]["max"]:,} ISK'  # noqa: E501

                    if (
                        market_json["appraisal"]["items"][0]["prices"]["buy"][
                            "order_count"
                        ]
                        == 0
                    ):
                        market_buy_order_price = "No buy orders found"

                    embed.add_field(
                        name="Buy Order Price",
                        value=market_buy_order_price,
                        inline=True,
                    )
                else:
                    embed.add_field(
                        name="API Error",
                        value=(
                            "Couldn't not fetch the price for the {market_name} market."
                        ).format(market_name=market["name"]),
                        inline=False,
                    )
        else:
            embed = Embed(
                title="Price Lookup",
                color=Color.red(),
            )

            embed.add_field(
                name="Error",
                value=(
                    "You forget to enter an item you want to lookup the price for ..."
                ),
                inline=False,
            )

        return await ctx.send(embed=embed)


def setup(bot):
    """
    add the cogg
    :param bot:
    :return:
    """

    bot.add_cog(PriceCheck(bot))
