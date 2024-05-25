from aadiscordmultiverse import models as dmv_models

from django.test import TestCase
from django.utils import timezone

from allianceauth.services.modules.discord import models as core_models
from allianceauth.tests.auth_utils import AuthUtils


class AuthbotTestCase(TestCase):

    def setUp(cls):
        AuthUtils.disconnect_signals()
        cls.u1 = AuthUtils.create_user(
            "user_1"
        )
        AuthUtils.add_main_character(
            cls.u1,
            "Authbot1",
            1234,
            5678,
            "BareMetal",
            "BTL"
        )

        AuthUtils.connect_signals()

    def create_discord_user(self):
        return core_models.DiscordUser.objects.create(
            user=self.u1,
            uid=123456789,
            username="AuthBot",
            activated=timezone.now()
        )

    def create_dmv_server(self):
        return dmv_models.DiscordManagedServer.objects.create(
            guild_id=12121212,
            server_name="TestAuthBotServer",
        )

    def create_dmv_user(self, server=None):
        if not server:
            server = self.create_dmv_server()
        return dmv_models.MultiDiscordUser.objects.create(
            guild=server,
            user=self.u1,
            uid=123456789,
            username="AuthBot",
            activated=timezone.now()
        )
