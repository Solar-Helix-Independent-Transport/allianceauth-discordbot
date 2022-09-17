from django.apps import AppConfig

from . import __version__


class AADiscordBotConfig(AppConfig):
    name = 'aadiscordbot'
    label = 'aadiscordbot'
    verbose_name = f'Discord Bot v{__version__}'

    # def ready(self):
    #    import aadiscordbot.signals
