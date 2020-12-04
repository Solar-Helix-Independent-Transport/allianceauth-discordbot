import logging
import pendulum
import traceback
import re

import discord
import aadiscordbot

from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color
from django.conf import settings
from discord.utils import get

from .. import app_settings 
#log = logging.getLogger(__name__)

class About(commands.Cog):
    """
    All about me!
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def about(self, ctx):
        """
        All about the bot
        """
        await ctx.trigger_typing()

        embed = Embed(title="AuthBot: The Authening")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/icons/516758158748811264/ae3991584b0f800b181c936cfc707880.webp?size=128"
        )
        embed.colour = Color.blue()

        embed.description = "This is a multi-de-functional discord bot tailored specifically for Alliance Auth Shenanigans."
        regex = r"^(.+)\/d.+"

        matches = re.finditer(regex, settings.DISCORD_CALLBACK_URL, re.MULTILINE)

        for m in matches:
            url = m.groups()
        embed.set_footer(text="Lovingly developed for Init.™ by AaronKable")

        embed.add_field(
            name="Number of Servers:", value=len(self.bot.guilds), inline=True
        )
        embed.add_field(name="Unwilling Monitorees:", value=len(self.bot.users), inline=True)
        embed.add_field(
            name="Auth Link", value="[{}]({})".format(url[0], url[0]), inline=False
        )
        embed.add_field(
            name="Version", value="{}@{}".format(aadiscordbot.__version__, aadiscordbot.__branch__), inline=False
        )

        #embed.add_field(
        #    name="Creator", value="<@318309023478972417>", inline=False
        #)

        return await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def uptime(self, ctx):
        """
        Returns the uptime
        """
        if ctx.message.author.id not in app_settings.get_admins(): #https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
            return await ctx.message.add_reaction(chr(0x1F44E))

        await ctx.send(
            pendulum.now(tz="UTC").diff_for_humans(
                self.bot.currentuptime, absolute=True
            )
        )

    @commands.command(hidden=True)
    async def get_webhooks(self, ctx):
        """
        Returns the webhooks for the channel
        """
        if ctx.message.author.id not in app_settings.get_admins(): #https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
            return await ctx.message.add_reaction(chr(0x1F44E))

        hooks = await ctx.message.channel.webhooks()
        if len(hooks) ==0:
            name = "{}_webhook".format(ctx.message.channel.name.replace(" ", "_"))
            hook = await ctx.message.channel.create_webhook(
                        name=name
                    )
            await ctx.message.author.send("{} - {}".format(
                hook.name,
                hook.url
            ))

        else:
            for hook in hooks:
                await ctx.message.author.send("{} - {}".format(
                    hook.name,
                    hook.url
                ))

        return await ctx.message.delete()

    @commands.command(hidden=True)
    async def new_channel(self, ctx):
        """
        create a new channel in a category.
        """
        if ctx.message.author.id not in app_settings.get_admins(): #https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
            return await ctx.message.add_reaction(chr(0x1F44E))

        await ctx.message.channel.trigger_typing()
        
        input_string = ctx.message.content[13:].split(' ')
        if len(input_string) != 2:
            return await ctx.message.add_reaction(chr(0x274C))

        everyone_role = ctx.guild.default_role
        channel_name = input_string[1]
        target_cat = get(ctx.guild.channels, id=int(input_string[0]))

        found_channel=False

        for channel in ctx.guild.channels:   # TODO replace with channel lookup not loop
                    if channel.name.lower() == channel_name.lower():
                        found_channel=True

        if not found_channel:
            channel = await ctx.guild.create_text_channel(channel_name.lower(),
                                                          category=target_cat) # make channel

            await channel.set_permissions(everyone_role, read_messages=False,
                                                         send_messages=False)

        return await ctx.message.add_reaction(chr(0x1F44D))


    @commands.command(hidden=True)
    async def add_role(self, ctx):
        """
        add a role from a channel.
        """
        if ctx.message.author.id not in app_settings.get_admins(): #https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
            return await ctx.message.add_reaction(chr(0x1F44E))

        await ctx.message.channel.trigger_typing()
        
        input_string = ctx.message.content[10:].split(' ')
        if len(input_string) != 2:
            return await ctx.message.add_reaction(chr(0x274C))

        target_role = get(ctx.guild.roles, name=input_string[1])
        channel_name = get(ctx.guild.channels, name=input_string[0])

        if channel_name:
            await channel_name.set_permissions(target_role, read_messages=True,
                                                             send_messages=True)

        return await ctx.message.add_reaction(chr(0x1F44D))

    @commands.command(hidden=True)
    async def rem_role(self, ctx):
        """
        remove a role from a channel.
        """
        if ctx.message.author.id not in app_settings.get_admins(): #https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
            return await ctx.message.add_reaction(chr(0x1F44E))

        await ctx.message.channel.trigger_typing()
        
        input_string = ctx.message.content[10:].split(' ')
        if len(input_string) != 2:
            return await ctx.message.add_reaction(chr(0x274C))

        target_role = get(ctx.guild.roles, name=input_string[1])
        channel_name = get(ctx.guild.channels, name=input_string[0])

        if channel_name:
            await channel_name.set_permissions(target_role, read_messages=False,
                                                             send_messages=False)

        return await ctx.message.add_reaction(chr(0x1F44D))

def setup(bot):
    bot.add_cog(About(bot))
""