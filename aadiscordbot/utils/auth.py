"""
    Utils for translating between auth and py-cord users

    Current Supported Auth service modules:
    - allianceauth.services.modules.discord
      - https://gitlab.com/allianceauth/allianceauth/
    - aadiscordmultiverse
      - https://github.com/Solar-Helix-Independent-Transport/allianceauth-discord-multiverse

"""

import logging

from discord import Guild, User

from django.conf import settings

from allianceauth.services.modules.discord.models import DiscordUser

logger = logging.getLogger(__name__)

DMV_ACTIVE = False

try:
    from aadiscordmultiverse.models import (
        DiscordManagedServer, MultiDiscordUser,
    )
except ImportError:
    logger.debug("DMV not installed")
    DMV_ACTIVE = False


def get_dmv_discord_user(user_id, guild_id):
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


def check_for_dmv_user(user: User, guild: Guild):
    """
        Return `True` if a discord user is authenticated to
        the DMV service module `False` Otherwise
    """
    user = get_dmv_discord_user(user.id, guild.id)
    if user:
        return True
    else:
        return False


def get_auth_discord_user(user_id):
    try:
        return DiscordUser.objects.get(uid=user_id)
    except DiscordUser.DoesNotExist:
        return None


def check_for_core_user(user: User):
    """
        Return `True` if a discord user is authenticated to
        the core auth service module `False` Otherwise
    """
    user = get_auth_discord_user(user.id)
    if user:
        return True
    else:
        return False


def guild_is_core_module(guild_id):
    """
        Check if the guild_id matches the core auth service module's guild
    """
    return id == getattr(settings, "DISCORD_GUILD_ID", -1)


def guild_is_dmv_module(guild_id):
    """
        Check if the guild_id matches the any of the DMV servers
    """
    guild = get_dmv_guild(guild_id)
    if guild:
        return True
    else:
        return False


def get_dmv_guild(guild_id):
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


def user_is_authenticated(user: User, guild: Guild):
    """
        Return `True` if a discord user is authenticated to the
        any service module `False` Otherwise

        Checks these services depending on the guild_id
    """
    if guild_is_core_module(guild.id):
        return check_for_core_user(user)

    elif guild_is_dmv_module(guild.id):
        return check_for_dmv_user(user, guild)

    else:
        return False


def get_auth_user(user: User, guild: Guild):
    """
        Get auth user from any service module
    """
    discord_user = None
    if guild_is_core_module(guild.id):
        discord_user = get_auth_discord_user(user.id)

    elif guild_is_dmv_module(guild.id):
        discord_user = get_dmv_discord_user(user.id, guild.id)

    if discord_user:
        return discord_user.user
    else:
        return None
