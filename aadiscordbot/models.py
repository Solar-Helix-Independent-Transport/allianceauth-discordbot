from allianceauth.services.modules.discord.models import DiscordUser
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class DiscordBot(models.Model):
    """Meta model for app permissions"""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ('basic_access', 'Can access this app'),
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
        except:
            b = self.emoji_text
        return f'{self.message.name}: {b} ({self.group})'


class AuthBotConfiguration(models.Model):

    admin_users = models.ManyToManyField(DiscordUser, blank=True)

    def __str__(self):
        return "AuthBot Configuration"

    def save(self, *args, **kwargs):
        if not self.pk and AuthBotConfiguration.objects.exists():
            # Force a single object
            raise ValidationError(
                'Only one Settings Model can there be at a time! No Sith Lords there are here!')
        self.pk = self.id = 1  # If this happens to be deleted and recreated, force it to be 1
        return super().save(*args, **kwargs)

# class WelcomeGoodbyeBinding(models.Model):
#     welcome_channel = models.ForeignKey("app.Model", verbose_name=_(""), on_delete=models.CASCADE)
#     goodbye_channel = models.ForeignKey("app.Model", verbose_name=_(""), on_delete=models.CASCADE)

#     def __str__(self):
#         return "Welcome and Goodbye Message Configuration"

#     def save(self, *args, **kwargs):
#         if not self.pk and AuthBotConfiguration.objects.exists():
#             # Force a single object
#             raise ValidationError(
#                 'Only one Settings Model can there be at a time! No Sith Lords there are here!')
#         self.pk = self.id = 1  # If this happens to be deleted and recreated, force it to be 1
#         return super().save(*args, **kwargs)
# We can use discord guild.system_channel


class WelcomeMessage(models.Model):
    message = models.TextField(_("Welcome Message"))
    authenticated = models.BooleanField(_("Valid for Authenticated Users"))
    unauthenticated = models.BooleanField(
        _("Valid for Un-Authenticated Users"))

    class Meta:
        default_permissions = ()
        verbose_name = 'Welcome Message'
        verbose_name_plural = 'Welcome Messages'


class GoodbyeMessage(models.Model):
    message = models.TextField(_("Goodbye Message"))
    authenticated = models.BooleanField(_("Valid for Authenticated Users"))
    unauthenticated = models.BooleanField(
        _("Valid for Un-Authenticated Users"))

    class Meta:
        default_permissions = ()
        verbose_name = 'Goodbye Message'
        verbose_name_plural = 'Goodbye Messages'
