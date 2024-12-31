from django.core.management.base import BaseCommand

from aadiscordbot import launcher


class Command(BaseCommand):
    help = 'Run Authbot'

    def handle(self, *args, **options):
        launcher.run_bot()
