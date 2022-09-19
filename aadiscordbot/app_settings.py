import re
from inspect import getgeneratorlocals

from django.apps import apps
from django.conf import settings


def get_site_url():  # regex sso url
    regex = r"^(.+)\/s.+"
    matches = re.finditer(regex, settings.ESI_SSO_CALLBACK_URL, re.MULTILINE)
    url = "http://"

    for m in matches:
        url = m.groups()[0]  # first match

    return url


def aastatistics_active():
    return apps.is_installed("aastatistics")


def timezones_active():
    return apps.is_installed("timezones")


def timerboard_active():
    return apps.is_installed("allianceauth.timerboard")


def get_admins():
    from .models import AuthBotConfiguration
    return list(AuthBotConfiguration.objects.get(pk=1).admin_users.all().values_list('uid', flat=True))


def get_low_adm():
    adm = getattr(settings, 'DISCORD_BOT_LOW_ADM', 2.5)
    if isinstance(adm, (float, int)):
        if adm < 0 or adm > 6:
            return 4.5
        else:
            return adm


def mumble_active():
    return apps.is_installed("allianceauth.services.modules.mumble")


def discord_active():
    return apps.is_installed('allianceauth.services.modules.discord')


DISCORD_BOT_PREFIX = getattr(settings, 'DISCORD_BOT_PREFIX', '!')

DISCORD_BOT_COGS = getattr(settings, 'DISCORD_BOT_COGS', ["aadiscordbot.cogs.about",
                                                          "aadiscordbot.cogs.admin",
                                                          "aadiscordbot.cogs.members",
                                                          "aadiscordbot.cogs.timers",
                                                          "aadiscordbot.cogs.auth",
                                                          "aadiscordbot.cogs.sov",
                                                          "aadiscordbot.cogs.time",
                                                          "aadiscordbot.cogs.eastereggs",
                                                          "aadiscordbot.cogs.remind",
                                                          "aadiscordbot.cogs.reaction_roles",
                                                          "aadiscordbot.cogs.services",
                                                          "aadiscordbot.cogs.price_check",
                                                          "aadiscordbot.cogs.eightball",
                                                          "aadiscordbot.cogs.welcomegoodbye",
                                                          "aadiscordbot.cogs.models",
                                                          "aadiscordbot.cogs.quote",
                                                          ]
                                                          )

DISCORD_BOT_ACCESS_DENIED_REACT = getattr(
    settings, 'DISCORD_BOT_ACCESS_DENIED_REACT', 0x1F44E)

# Deprecated. use Decorators or get_admins()
DISCORD_BOT_ADMIN_USER = getattr(settings, 'DISCORD_BOT_ADMIN_USER', [])

ADMIN_DISCORD_BOT_CHANNELS = getattr(
    settings, 'ADMIN_DISCORD_BOT_CHANNELS', [])
SOV_DISCORD_BOT_CHANNELS = getattr(settings, 'SOV_DISCORD_BOT_CHANNELS', [])
ADM_DISCORD_BOT_CHANNELS = getattr(settings, 'ADM_DISCORD_BOT_CHANNELS', [])

DISCORD_BOT_SOV_STRUCTURE_OWNER_IDS = getattr(
    settings, 'DISCORD_BOT_SOV_STRUCTURE_OWNER_IDS', [])
DISCORD_BOT_MEMBER_ALLIANCES = getattr(
    settings, 'DISCORD_BOT_MEMBER_ALLIANCES', [])
DISCORD_BOT_ADM_REGIONS = getattr(settings, 'DISCORD_BOT_ADM_REGIONS', [])
DISCORD_BOT_ADM_SYSTEMS = getattr(settings, 'DISCORD_BOT_ADM_SYSTEMS', [])
DISCORD_BOT_ADM_CONSTELLATIONS = getattr(
    settings, 'DISCORD_BOT_ADM_CONSTELLATIONS', [])

DISCORD_BOT_MESSAGE_INTENT = getattr(
    settings, 'DISCORD_BOT_MESSAGE_INTENT', True)

DISCORD_BOT_TOKEN = getattr(
    settings, 'AUTHBOT_DISCORD_BOT_TOKEN', getattr(
        settings, 'DISCORD_BOT_TOKEN', None))

DISCORD_APP_ID = getattr(
    settings, 'AUTHBOT_DISCORD_APP_ID', getattr(
        settings, 'DISCORD_APP_ID', None))


DISCORD_BOT_TASK_RATE_LIMITS = getattr(settings, 'DISCORD_BOT_TASK_RATE_LIMITS',
                                       {"send_channel_message_by_discord_id": "100/s",
                                        "send_direct_message_by_discord_id": "100/s",
                                        "send_direct_message_by_user_id": "100/s"})
