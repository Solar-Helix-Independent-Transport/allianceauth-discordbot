from django.apps import AppConfig
from . import __version__


class AADiscordBotConfig(AppConfig):
    name = 'aadiscordbot'
    label = 'aadiscordbot'
    verbose_name = 'Discord Bot v{}'.format(__version__)

    # def ready(self):
    #    import aadiscordbot.signals
