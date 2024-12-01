from unittest.mock import MagicMock, patch

from aadiscordbot.cogs.utils.exceptions import NotAuthenticated

from ..app_settings import discord_active, dmv_active
from ..models import AuthBotConfiguration
from ..utils import auth
from . import AuthbotTestCase


class TestUtilsAuth(AuthbotTestCase):

    def test_dmv_active_pass(self):
        self.assertTrue(dmv_active())

    def test_dmv_active_fail(self):
        with self.modify_settings(
            INSTALLED_APPS={
                "remove": [
                    "aadiscordmultiverse"
                ]
            }
        ):
            self.assertFalse(dmv_active())

    def test_discord_active_pass(self):
        self.assertTrue(discord_active())

    def test_discord_active_fail(self):
        with self.modify_settings(
            INSTALLED_APPS={
                "remove": [
                    "allianceauth.services.modules.discord"
                ]
            }
        ):
            self.assertFalse(discord_active())

    """
        DMV User Section
    """
    @patch('aadiscordbot.utils.auth.DMV_ACTIVE', False)
    def test_get_dmv_discord_user_no_module(self):
        self.assertIsNone(auth._get_dmv_discord_user(123, 123))

    def test_get_dmv_discord_user_no_user(self):
        self.create_dmv_user()
        self.assertIsNone(auth._get_dmv_discord_user(123, 123))

    def test_get_dmv_discord_user_valid(self):
        user = self.create_dmv_user()
        self.assertEqual(
            auth._get_dmv_discord_user(user.uid, user.guild.guild_id),
            user
        )

    @patch('aadiscordbot.utils.auth.DMV_ACTIVE', False)
    def test_check_for_dmv_user_no_module(self):
        usr = MagicMock()
        usr.id = 1234
        gld = MagicMock()
        gld.id = 4567
        self.assertFalse(auth._check_for_dmv_user(usr, gld))

    def test_check_for_dmv_user_no_user(self):
        self.create_dmv_user()
        usr = MagicMock()
        usr.id = 1234
        gld = MagicMock()
        gld.id = 4567
        self.assertFalse(auth._check_for_dmv_user(usr, gld))

    def test_check_for_dmv_user(self):
        user = self.create_dmv_user()
        usr = MagicMock()
        usr.id = user.uid
        gld = MagicMock()
        gld.id = user.guild.guild_id
        self.assertTrue(auth._check_for_dmv_user(usr, gld))

    """
        Core Module User Section
    """
    @patch('aadiscordbot.utils.auth.DISCORD_ACTIVE', False)
    def test_get_core_discord_user_no_module(self):
        self.assertIsNone(auth._get_core_discord_user(123))

    def test_get_core_discord_user_no_user(self):
        self.create_discord_user()
        self.assertIsNone(auth._get_core_discord_user(123))

    def test_get_core_discord_user_valid(self):
        user = self.create_discord_user()
        self.assertEqual(
            auth._get_core_discord_user(user.uid),
            user
        )

    @patch('aadiscordbot.utils.auth.DISCORD_ACTIVE', False)
    def test_check_for_core_user_no_module(self):
        usr = MagicMock()
        usr.id = 1234
        self.assertFalse(auth._check_for_core_user(usr))

    def test_check_for_core_user_no_user(self):
        usr = MagicMock()
        usr.id = 1234
        self.assertFalse(auth._check_for_core_user(usr))

    def test_check_for_core_user(self):
        user = self.create_discord_user()
        usr = MagicMock()
        usr.id = user.uid
        self.assertTrue(
            auth._check_for_core_user(usr),
        )

    """
        Server Section
    """
    @patch('aadiscordbot.utils.auth.DISCORD_ACTIVE', False)
    def test_guild_is_core_module_no_module(self):
        self.assertFalse(auth._guild_is_core_module(1234))

    def test_guild_is_core_module_not_guild(self):
        self.assertFalse(auth._guild_is_core_module(1234))

    def test_guild_is_core_module(self):
        self.assertTrue(
            auth._guild_is_core_module(1234567891011),
        )

    @patch('aadiscordbot.utils.auth.DMV_ACTIVE', False)
    def test_guild_is_dmv_module_no_module(self):
        self.assertFalse(auth._guild_is_dmv_module(1234))

    def test_guild_is_dmv_module_not_guild(self):
        self.assertFalse(auth._guild_is_dmv_module(1234))

    def test_guild_is_dmv_module(self):
        gld = self.create_dmv_server()
        self.assertTrue(
            auth._guild_is_dmv_module(gld.guild_id),
        )

    @patch('aadiscordbot.utils.auth.DMV_ACTIVE', False)
    @patch('aadiscordbot.utils.auth.DISCORD_ACTIVE', False)
    def test_is_guild_managed_no_modules(self):
        gld = MagicMock()
        gld.id = 1234
        self.assertFalse(auth.is_guild_managed(gld))

    @patch('aadiscordbot.utils.auth.DMV_ACTIVE', True)
    @patch('aadiscordbot.utils.auth.DISCORD_ACTIVE', False)
    def test_is_guild_managed_dnv_not_guild(self):
        self.create_dmv_server()
        gld = MagicMock()
        gld.id = 1234
        self.assertFalse(auth.is_guild_managed(gld))

    @patch('aadiscordbot.utils.auth.DMV_ACTIVE', True)
    @patch('aadiscordbot.utils.auth.DISCORD_ACTIVE', False)
    def test_is_guild_managed_dnv_is_guild(self):
        guild = self.create_dmv_server()
        gld = MagicMock()
        gld.id = guild.guild_id
        self.assertTrue(auth.is_guild_managed(gld))

    @patch('aadiscordbot.utils.auth.DMV_ACTIVE', False)
    @patch('aadiscordbot.utils.auth.DISCORD_ACTIVE', True)
    def test_is_guild_managed_core_not_guild(self):
        gld = MagicMock()
        gld.id = 1234
        self.assertFalse(auth.is_guild_managed(gld))

    @patch('aadiscordbot.utils.auth.DMV_ACTIVE', False)
    @patch('aadiscordbot.utils.auth.DISCORD_ACTIVE', True)
    def test_is_guild_managed_core_is_guild(self):
        gld = MagicMock()
        gld.id = 1234567891011
        self.assertTrue(auth.is_guild_managed(gld))

    """
        Auth User Section
    """

    @patch('aadiscordbot.utils.auth.DISCORD_ACTIVE', False)
    def test_user_is_authenticated(self):
        user = self.create_dmv_user()

        usr = MagicMock()
        usr.id = user.uid
        gld = MagicMock()
        gld.id = user.guild.guild_id
        self.assertTrue(auth.user_is_authenticated(usr, gld))

    def test_is_user_authenticated_dnv(self):
        user = self.create_dmv_user()
        usr = MagicMock()
        usr.id = user.uid
        gld = MagicMock()
        gld.id = user.guild.guild_id

        self.assertTrue(auth.is_user_authenticated(usr, gld))

    def test_is_user_authenticated_core(self):
        user = self.create_discord_user()
        usr = MagicMock()
        usr.id = user.uid
        gld = MagicMock()
        gld.id = 1234567891011

        self.assertTrue(auth.is_user_authenticated(usr, gld))

    def test_is_user_authenticated_none(self):
        usr = MagicMock()
        usr.id = 123456789
        gld = MagicMock()
        gld.id = 12345678910

        self.assertFalse(auth.is_user_authenticated(usr, gld))

    def test_get_auth_user_core(self):
        user = self.create_discord_user()
        usr = MagicMock()
        usr.id = user.uid
        gld = MagicMock()
        gld.id = 1234567891011

        self.assertEqual(
            auth.get_auth_user(usr, gld),
            self.u1
        )

    def test_get_auth_user_dnv(self):
        user = self.create_dmv_user()
        usr = MagicMock()
        usr.id = user.uid
        gld = MagicMock()
        gld.id = user.guild.guild_id

        self.assertEqual(
            auth.get_auth_user(usr, gld),
            self.u1
        )

    def test_get_auth_user_none(self):
        usr = MagicMock()
        usr.id = 1234
        gld = MagicMock()
        gld.id = 5678

        with self.assertRaises(NotAuthenticated):
            auth.get_auth_user(usr, gld)

    def test_bot_admin_fail(self):
        user = self.create_discord_user()
        usr = MagicMock()
        usr.id = user.uid

        self.assertFalse(auth.is_user_bot_admin(usr))

    def test_bot_admin_pass(self):
        user = self.create_discord_user()
        AuthBotConfiguration.objects.get(id=1).admin_users.add(user)
        usr = MagicMock()
        usr.id = user.uid

        self.assertTrue(auth.is_user_bot_admin(usr))

    def test_get_discord_user_core(self):
        user = self.create_discord_user()
        self.assertEqual(
            auth.get_discord_user_id(self.u1),
            user.uid
        )

    def test_get_discord_user_dnv(self):
        user = self.create_dmv_user()
        self.assertEqual(
            auth.get_discord_user_id(self.u1),
            user.uid
        )

    def test_get_discord_user_none(self):
        with self.assertRaises(NotAuthenticated):
            auth.get_discord_user_id(self.u2)
