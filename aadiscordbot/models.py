import json

from solo.models import SingletonModel

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from allianceauth.services.modules.discord.models import DiscordUser


class DiscordBot(models.Model):
    """Meta model for app permissions"""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ('basic_access', 'Can access this app.'),
            ('member_command_access', 'can access the member commands.')
        )


class Servers(models.Model):
    """Servers and their ID"""

    server = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Server'
        verbose_name_plural = 'Servers'

    def __str__(self):
        return f'{self.name}'


class Channels(models.Model):
    """Channel IDs, Names and the Server they belong to"""

    server = models.ForeignKey(Servers, on_delete=models.CASCADE)
    channel = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    deleted = models.BooleanField(_("Deleted"), default=False)

    def __str__(self):
        return f'"{self.name}" On "{self.server.name}"'

    class Meta:
        verbose_name = 'Channel'
        verbose_name_plural = 'Channels'


class ReactionRoleMessage(models.Model):
    """Reaction Role Handler"""

    message = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    non_auth_users = models.BooleanField(
        default=False, help_text="Can Non Authed/public discord members gain groups from this Reaction Roles Message")

    def __str__(self):
        return f'{self.name}'

    class Meta:
        permissions = (
            ('manage_reactions', 'Can Manage Reaction Roles'),
        )


class ReactionRoleBinding(models.Model):
    """Reaction Links"""

    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, null=True, default=None)
    emoji = models.CharField(max_length=100)
    emoji_text = models.CharField(max_length=100)
    message = models.ForeignKey(ReactionRoleMessage, on_delete=models.CASCADE)

    def __str__(self):
        try:
            b = eval(self.emoji_text).decode('utf-8')
        except Exception:
            b = self.emoji_text
        return f'{self.message.name}: {b} ({self.group})'


class AuthBotConfiguration(models.Model):

    admin_users = models.ManyToManyField(DiscordUser, blank=True)

    admin_user_ids = models.TextField(default=None, null=True, blank=True)

    def get_non_model_admin_ids(self):
        try:
            ids = self.admin_user_ids.split(",")
            return [
                int(id) for id in ids
            ]
        except Exception:
            return []

    def __str__(self):
        return "AuthBot Configuration"

    def save(self, *args, **kwargs):
        if not self.pk and AuthBotConfiguration.objects.exists():
            # Force a single object
            raise ValidationError(
                'Only one Settings Model can there be at a time! No Sith Lords there are here!')
        self.pk = self.id = 1  # If this happens to be deleted and recreated, force it to be 1
        return super().save(*args, **kwargs)


class WelcomeMessage(models.Model):
    message = models.TextField(_("Welcome Message"))
    authenticated = models.BooleanField(_("Valid for Authenticated Users"))
    unauthenticated = models.BooleanField(
        _("Valid for Un-Authenticated Users"))
    guild_id = models.BigIntegerField(default=None, null=True, blank=True)

    class Meta:
        default_permissions = ()
        verbose_name = 'Welcome Message'
        verbose_name_plural = 'Welcome Messages'


class GoodbyeMessage(models.Model):
    message = models.TextField(_("Goodbye Message"))
    authenticated = models.BooleanField(_("Valid for Authenticated Users"))
    unauthenticated = models.BooleanField(
        _("Valid for Un-Authenticated Users"))
    guild_id = models.BigIntegerField(default=None, null=True, blank=True)

    class Meta:
        default_permissions = ()
        verbose_name = 'Goodbye Message'
        verbose_name_plural = 'Goodbye Messages'


class QuoteMessage(models.Model):
    """A saved discord message, Used by the Quote cog"""
    server = models.ForeignKey(Servers, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channels, on_delete=models.CASCADE)
    message = models.BigIntegerField(primary_key=True)
    content = models.CharField(max_length=1000)
    datetime = models.DateTimeField(blank=True, null=True)
    author = models.PositiveBigIntegerField()
    author_nick = models.CharField(max_length=50, blank=True, null=True)
    reference = models.CharField(
        max_length=100, help_text="Nickname for this quote")

    class Meta:
        default_permissions = ()
        verbose_name = 'Quote Message'
        verbose_name_plural = 'Quote Messages'
        permissions = (
            ('quote_save', 'Can save quotes'),
        )


class TicketGroups(SingletonModel):
    groups = models.ManyToManyField(
        Group, blank=True, help_text="Pingable groups for ticketing")
    ticket_channel = models.ForeignKey(
        Channels, on_delete=models.SET_NULL, null=True, default=None, blank=True)

    ticket_channels = models.TextField(
        default=None,
        null=True,
        blank=True,
        help_text="JSON dictionary {server_id:channel_id}")

    class Meta:
        default_permissions = ()
        verbose_name = 'Ticket Cog Configuration'
        verbose_name_plural = 'Ticket Cog Configuration'

    def __str__(self):
        return "Ticket Cog Configuration"

    def get_channel_for_server(self, server_id):
        try:
            channels = json.loads(self.ticket_channels)
            channel_id = channels.get(str(server_id), 0)
            return channel_id if channel_id else None
        except json.JSONDecodeError:
            if self.ticket_channel:
                return self.ticket_channel.channel
            else:
                return None
