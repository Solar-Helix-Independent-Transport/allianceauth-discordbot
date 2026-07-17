"""
Django system checks for AA Discordbot
"""

from django.conf import settings
from django.core.checks import CheckMessage, Warning, register

"""
A = idk first one i guess
"""


@register()
def django_settings(app_configs, **kwargs) -> list[CheckMessage]:
    """
    Check that Django settings are correctly configured

    :param app_configs:
    :type app_configs:
    :param kwargs:
    :type kwargs:
    :return:
    :rtype:
    """

    checks: list[CheckMessage] = []

    if hasattr(settings, "DISCORD_BOT_ADMIN_USER"):
        checks.append(
            Warning(
                msg="'DISCORD_BOT_ADMIN_USER' is deprecated and not actively used",
                hint="Please migrate Users and user_ids to AuthbotConfigration SingletonModel",
                id="discordbot.checks.A001",
            )
        )

    return checks
