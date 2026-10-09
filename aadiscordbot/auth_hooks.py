from allianceauth import hooks

from . import app_settings


@hooks.register('discord_cogs_hook')
def register_cogs():
    return app_settings.DISCORD_BOT_COGS
