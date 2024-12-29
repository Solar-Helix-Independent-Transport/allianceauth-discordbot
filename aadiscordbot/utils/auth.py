"""
    Utils for translating between auth and py-cord users

    Current Supported Auth service modules:
    - allianceauth.services.modules.discord
      - https://gitlab.com/allianceauth/allianceauth/
    - aadiscordmultiverse
      - https://github.com/Solar-Helix-Independent-Transport/allianceauth-discord-multiverse

"""

import logging
import warnings
from typing import Union

from discord import Guild, User

from django.conf import settings
from django.contrib.auth.models import User as AuthUser

from aadiscordbot.app_settings import discord_active, dmv_active, get_admins
from aadiscordbot.cogs.utils.exceptions import NotAuthenticated

logger = logging.getLogger(__name__)

DMV_ACTIVE = dmv_active()
DISCORD_ACTIVE = discord_active()


try:
    if DISCORD_ACTIVE:
        # this needs to be imported safely incase only DMV installed
        from allianceauth.services.modules.discord.models import DiscordUser
except ImportError:
    logger.debug("Discord not installed?")


try:
    if DMV_ACTIVE:
        # this needs to be imported safely incase only Core service installed
        from aadiscordmultiverse.models import (
            DiscordManagedServer, MultiDiscordUser,
        )
except ImportError:
    logger.debug("DMV not installed?")


def _get_dmv_discord_user(user_id, guild_id):
    if DMV_ACTIVE:
        try:
            return MultiDiscordUser.objects.get(
                guild_id=guild_id,
                uid=user_id
            )
        except MultiDiscordUser.DoesNotExist:
            return None
    else:
        return None


def _get_any_dmv_discord_user(user_id):
    if DMV_ACTIVE:
        try:
            return MultiDiscordUser.objects.filter(
                uid=user_id
            ).first()
        except MultiDiscordUser.DoesNotExist:
            return None
    else:
        return None


def _check_for_dmv_user(user: User, guild: Guild):
    """
        Return `True` if a discord user is authenticated to
        the DMV service module `False` Otherwise
    """
    user = _get_dmv_discord_user(user.id, guild.id)
    if user:
        return True
    else:
        return False


def _get_core_discord_user(user_id):
    if DISCORD_ACTIVE:
        try:
            return DiscordUser.objects.get(uid=user_id)
        except DiscordUser.DoesNotExist:
            return None
    else:
        return None


def _check_for_core_user(user: User):
    """
        Return `True` if a discord user is authenticated to
        the core auth service module `False` Otherwise
    """
    user = _get_core_discord_user(user.id)
    if user:
        return True
    else:
        return False


def _guild_is_core_module(guild_id):
    """
        Check if the guild_id matches the core auth service module's guild
    """
    # May be string in settings so cast to int for check.
    # discord returns int for guild.id
    gid = int(getattr(settings, "DISCORD_GUILD_ID", -1))

    return guild_id == gid and DISCORD_ACTIVE


def _guild_is_dmv_module(guild_id):
    """
        Check if the guild_id matches the any of the DMV servers
    """
    guild = _get_dmv_guild(guild_id)
    if guild:
        return True
    else:
        return False


def _get_dmv_guild(guild_id):
    """
        Return DMV Guild model if DMV installed and
    """
    if DMV_ACTIVE:
        try:
            return DiscordManagedServer.objects.get(
                guild_id=guild_id,
            )
        except DiscordManagedServer.DoesNotExist:
            return None
    else:
        return None


def is_user_bot_admin(user: User):
    """
        Is user a configured Bot Admin
        TODO: Make this work with DNV somehow.
    """
    if user.id in get_admins():
        return True
    else:
        return False


def is_guild_managed(guild: Guild):
    core = _guild_is_core_module(guild.id)
    dmv = _guild_is_dmv_module(guild.id)
    return core or dmv


def user_is_authenticated(user: User, guild: Guild):
    warnings.warn(
        "user_is_authenticated is deprecated use is_user_authenticated instead",
        DeprecationWarning,
        stacklevel=2
    )
    logger.warning("user_is_authenticated is deprecated use is_user_authenticated instead")
    return is_user_authenticated(user, guild)


def is_user_authenticated(user: User, guild: Guild):
    """
        Return `True` if a discord user is authenticated to the
        any service module `False` Otherwise

        Checks these services depending on the guild_id
    """
    if _guild_is_core_module(guild.id):
        return _check_for_core_user(user)

    elif _guild_is_dmv_module(guild.id):
        return _check_for_dmv_user(user, guild)

    else:
        return False


def get_auth_user(user: Union[User, int], guild: Union[Guild, int] = None) -> User:
    """
        Get auth user from any Discord Service
        raises NotAuthenticated if user is not found.
    """
    guild_id = None
    user_id = None

    if isinstance(user, int):
        user_id = user
    else:
        user_id = user.id

    if guild:
        if isinstance(guild, int):
            guild_id = guild
        else:
            guild_id = guild.id

    discord_user = None

    if _guild_is_core_module(guild_id):
        discord_user = _get_core_discord_user(user_id)

    elif _guild_is_dmv_module(guild_id):
        discord_user = _get_dmv_discord_user(user_id, guild_id)

    else:
        discord_user = _get_any_dmv_discord_user(user_id)

    if discord_user:
        return discord_user.user
    else:
        raise NotAuthenticated


def get_discord_user_id(user: Union[AuthUser, int]) -> int:
    """
        Get discord_id from any Discord Service
        raises NotAuthenticated if user is not found.
    """
    user_id = None

    if isinstance(user, int):
        user_id = user
    else:
        user_id = user.id

    discord_user = None

    if DISCORD_ACTIVE:
        try:
            discord_user = DiscordUser.objects.get(user_id=user_id)
        except DiscordUser.DoesNotExist:
            pass
    if not discord_user and DMV_ACTIVE:
        try:
            discord_user = MultiDiscordUser.objects.filter(user_id=user_id).first()
        except MultiDiscordUser.DoesNotExist:
            pass

    if discord_user:
        return discord_user.uid
    else:
        raise NotAuthenticated
