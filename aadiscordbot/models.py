from django.conf import settings
from django.db import models
from django.contrib.auth.models import Group


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
        return '{}'.format(self.name)


class Channels(models.Model):
    """Channel IDs, Names and the Server they belong to"""

    server = models.ForeignKey(Servers, on_delete=models.CASCADE)
    channel = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return '"{}" On "{}"'.format(self.name, self.server.name)

    class Meta:
        verbose_name = 'Channel'
        verbose_name_plural = 'Channels'


class ReactionRoleMessage(models.Model):
    """Reaction Role Handler"""

    message = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        permissions = ( 
            ('manage_reactions', 'Can Manage Reaction Roles'), 
        )


class ReactionRoleBinding(models.Model):
    """Reaction Links"""

    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, default=None)
    emoji = models.CharField(max_length=100)
    emoji_text = models.CharField(max_length=100)
    message = models.ForeignKey(ReactionRoleMessage, on_delete=models.CASCADE)

    def __str__(self):
        return '{}: {} ({})'.format(self.message.name, self.emoji_text, self.group)
