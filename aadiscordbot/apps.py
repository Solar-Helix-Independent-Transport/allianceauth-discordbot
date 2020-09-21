from django.apps import AppConfig
from . import __version__

class AADiscordBotConfig(AppConfig):
    name = 'aadiscordbot'
    label = 'aadiscordbot'
    verbose_name = 'AA Discordbot v{}'.format(__version__)