# Cog Stuff
import django.core.exceptions
from allianceauth.authentication.models import State
from allianceauth.eveonline.models import EveAllianceInfo, EveCorporationInfo
from discord.colour import Color
from discord.embeds import Embed
from discord.ext import commands
from django.contrib.auth.models import User

# AA Contexts
from aadiscordbot.app_settings import DISCORD_BOT_ADMIN_USER, get_site_url
from aadiscordbot.cogs.utils.decorators import sender_is_admin

from ..app_settings import discord_active, mumble_active

if discord_active:
    from allianceauth.services.modules.discord.models import DiscordUser

if mumble_active:
    from allianceauth.services.modules.mumble.auth_hooks import MumbleUser

import logging

logger = logging.getLogger(__name__)


class Services(commands.Cog):
    """
    Commands to manage Services Access
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @sender_is_admin()
    async def services(self, ctx):
        """
        service_registration STATE
        """
        await ctx.trigger_typing()
        await ctx.send('Checking for Users without Service Activation')
        await ctx.trigger_typing()

        input_state = State.objects.get(name=ctx.message.content[10:])
        try:
            user_list = User.objects.filter(profile__state=input_state.id)
        except Exception as e:
            logger.error(e)

        if mumble_active():
            payload = "The Following Users don't have Mumble \n"
            for user in user_list:
                if user.has_perm('mumble.can_access'):
                    try:
                        MumbleUser.objects.get(user=user)
                    except django.core.exceptions.ObjectDoesNotExist:
                        if len(payload) > 1000:
                            try:
                                await ctx.send(payload)
                                payload = "The Following Users don't have Mumble \n"
                            except Exception as e:
                                logger.error(e)
                        # keep building the payload
                        payload = payload + user.profile.main_character.character_name + \
                            "(" + user.profile.main_character.corporation_ticker + ")" + "\n"
            try:
                await ctx.send(payload)
            except Exception as e:
                logger.error(e)
                payload = "No State found for that Search"
                return await ctx.send(payload)

        if discord_active():
            payload = "The Following Users don't have Discord \n"
            for user in user_list:
                if user.has_perm('discord.can_access'):
                    try:
                        DiscordUser.objects.get(user=user)
                    except django.core.exceptions.ObjectDoesNotExist:
                        if len(payload) > 1000:
                            try:
                                await ctx.send(payload)
                                payload = "The Following Users don't have Discord \n"
                            except Exception as e:
                                logger.error(e)
                        # keep building the payload
                        payload = payload + user.profile.main_character.character_name + \
                            "(" + user.profile.main_character.corporation_ticker + ")" + "\n"
            try:
                await ctx.send(payload)
            except Exception as e:
                logger.error(e)

    @commands.command(pass_context=True)
    @sender_is_admin()
    async def services_stats(self, ctx):
        """
        service_registration State>Alliance>Corp
        Returns Service Registration Statistics, similar to Corp Stats Two
        """
        mode = "None"
        try:
            input = EveCorporationInfo.objects.get(
                corporation_name=ctx.message.content[16:])
            mode = "Corp"
        except django.core.exceptions.ObjectDoesNotExist:
            pass

        try:
            input = EveAllianceInfo.objects.get(
                alliance_name=ctx.message.content[16:])
            mode = "Alliance"
        except django.core.exceptions.ObjectDoesNotExist:
            pass

        try:
            input = State.objects.get(name=ctx.message.content[16:])
            mode = "State"
        except django.core.exceptions.ObjectDoesNotExist:
            pass

        if mode == "Corp":
            try:
                user_list = User.objects.filter(
                    profile__main_character__corporation_id=input.id)
                payload = "Services Stats for Corporation " + input.corporation_name + "\n"
            except Exception as e:
                logger.error(e)
        elif mode == "Alliance":
            try:
                user_list = User.objects.filter(
                    profile__main_character__alliance_id=input.id)
                payload = "Services Stats for Alliance " + input.alliance_name + "\n"
            except Exception as e:
                logger.error(e)
        elif mode == "State":
            try:
                user_list = User.objects.filter(profile__state=input.id)
                payload = "Services Stats for State " + input.name + "\n"
            except Exception as e:
                logger.error(e)

        else:
            payload = "No State, Alliance or Corp found for that search"
            return await ctx.send(payload)

        if discord_active():
            activations_discord = 0
        if mumble_active():
            activations_mumble = 0

        for user in user_list:
            if discord_active():
                try:
                    DiscordUser.objects.get(user=user)
                    activations_discord + 1
                except django.core.exceptions.ObjectDoesNotExist:
                    pass
            if mumble_active():
                try:
                    MumbleUser.objects.get(user=user)
                    activations_mumble + 1
                except django.core.exceptions.ObjectDoesNotExist:
                    pass

        if mumble_active():
            payload = payload + "Mumble " + \
                str(activations_mumble) + " / " + str(len(user_list)) + "\n"
        if discord_active():
            payload = payload + "Discord " + \
                str(activations_discord) + " / " + str(len(user_list)) + "\n"

        try:
            await ctx.send(payload)
            payload = "The Following Users don't have Discord \n"
        except Exception as e:
            logger.error(e)


def setup(bot):
    bot.add_cog(Services(bot))
