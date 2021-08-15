from inspect import getgeneratorlocals
from django.conf import settings
from django.apps import apps
import re


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


def mumble_active():
    return 'allianceauth.services.modules.mumble' in settings.INSTALLED_APPS


def discord_active():
    return 'allianceauth.services.modules.discord' in settings.INSTALLED_APPS

DISCORD_BOT_PREFIX = getattr(settings, 'DISCORD_BOT_PREFIX', '!')

DISCORD_BOT_COGS = getattr(settings, 'DISCORD_BOT_COGS', ["aadiscordbot.cogs.about",
                                                          "aadiscordbot.cogs.members",
                                                          "aadiscordbot.cogs.timers",
                                                          "aadiscordbot.cogs.auth",
                                                          "aadiscordbot.cogs.sov",
                                                          "aadiscordbot.cogs.time",
                                                          "aadiscordbot.cogs.eastereggs",
                                                          "aadiscordbot.cogs.remind",
                                                          "aadiscordbot.cogs.price_check",
                                                          "aadiscordbot.cogs.reaction_roles"])

DISCORD_BOT_ACCESS_DENIED_REACT = getattr(settings, 'DISCORD_BOT_ACCESS_DENIED_REACT', 0x1F44E )

DISCORD_BOT_ADMIN_USER = getattr(settings, 'DISCORD_BOT_ADMIN_USER', [])

ADMIN_DISCORD_BOT_CHANNELS = getattr(settings, 'ADMIN_DISCORD_BOT_CHANNELS', [])
SOV_DISCORD_BOT_CHANNELS = getattr(settings, 'SOV_DISCORD_BOT_CHANNELS', [])
ADM_DISCORD_BOT_CHANNELS = getattr(settings, 'ADM_DISCORD_BOT_CHANNELS', [])

DISCORD_BOT_SOV_STRUCTURE_OWNER_IDS = getattr(settings, 'DISCORD_BOT_SOV_STRUCTURE_OWNER_IDS', [])
DISCORD_BOT_MEMBER_ALLIANCES = getattr(settings, 'DISCORD_BOT_MEMBER_ALLIANCES', [])
DISCORD_BOT_ADM_REGIONS = getattr(settings, 'DISCORD_BOT_ADM_REGIONS', [])
DISCORD_BOT_ADM_SYSTEMS = getattr(settings, 'DISCORD_BOT_ADM_SYSTEMS', [])
DISCORD_BOT_ADM_CONSTELLATIONS = getattr(settings, 'DISCORD_BOT_ADM_CONSTELLATIONS', [])

