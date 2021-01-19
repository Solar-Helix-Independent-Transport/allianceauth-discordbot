from django.conf import settings
import re


def get_site_url():  # regex sso url
    regex = r"^(.+)\/s.+"
    matches = re.finditer(regex, settings.ESI_SSO_CALLBACK_URL, re.MULTILINE)
    url = "http://"

    for m in matches:
        url = m.groups()[0]  # first match

    return url


def aastatistics_active():
    return 'aastatistics' in settings.INSTALLED_APPS


def timezones_active():
    return 'timezones' in settings.INSTALLED_APPS


def timerboard_active():
    return 'allianceauth.timerboard' in settings.INSTALLED_APPS


def get_admins():
    admin = getattr(settings, 'DISCORD_BOT_ADMIN_USER', [])
    if isinstance(admin, int):
        return [admin]
    else:
        return admin

DISCORD_BOT_COGS = getattr(settings, 'DISCORD_BOT_COGS',[ "aadiscordbot.cogs.about",
                                                          "aadiscordbot.cogs.members",
                                                          "aadiscordbot.cogs.timers",
                                                          "aadiscordbot.cogs.auth",
                                                          "aadiscordbot.cogs.sov",
                                                          "aadiscordbot.cogs.time",
                                                          "aadiscordbot.cogs.eastereggs",
                                                          "aadiscordbot.cogs.remind",])
