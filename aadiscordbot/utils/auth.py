import logging

from discord import Guild, User

from django.conf import settings

from allianceauth.services.modules.discord.models import DiscordUser

logger = logging.getLogger(__name__)


def check_for_dmv_user(user: User, guild: Guild):
    """
        Return `True` if a discord user is authenticated to
        the DMV service module `False` Otherwise
    """
    try:
        from aadiscordmultiverse.models import MultiDiscordUser
        try:
            MultiDiscordUser.objects.get(
                guild_id=guild.id,
                uid=user.id
            )
            return True
        except MultiDiscordUser.DoesNotExist:
            return False
    except ImportError:
        logger.debug("DMV not installed")
    return False


def check_for_core_user(user: User):
    """
        Return `True` if a discord user is authenticated to
        the core auth service module `False` Otherwise
    """
    try:
        DiscordUser.objects.get(uid=user.id)
        return True
    except DiscordUser.DoesNotExist:
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

    try:
        from aadiscordmultiverse.models import DiscordManagedServer
        try:
            DiscordManagedServer.objects.get(
                guild_id=guild_id,
            )
            return True
        except DiscordManagedServer.DoesNotExist:
            return False
    except ImportError:
        logger.debug("DMV not installed")
    return False


def user_is_authenticated(user: User, guild: Guild):
    """
        Return `True` if a discord user is authenticated to the
        any service module `False` Otherwise

        Checks these services depending on the guild_id
          - allianceauth.services.modules.discord
          - aadiscordmultiverse
    """
    if guild_is_core_module(guild.id):
        logger.debug("Core Auth discord service user")
        return check_for_core_user(user)

    elif guild_is_dmv_module(guild.id):
        logger.debug("Maybe a DMV managed server discord service user")
        return check_for_dmv_user(user, guild)

    else:
        logger.debug("Unknown User/Server/Configuration")
        return False
