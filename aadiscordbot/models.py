from django.conf import settings
from django.db import models


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


class Message(models.Model):
    """A saved discord message, Used by the Quote cog"""
    server = models.ForeignKey(Servers, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channels, on_delete=models.CASCADE)
    message = models.BigIntegerField(primary_key=True)
    content = models.CharField(max_length=1000)
    datetime = models.DateTimeField(blank=True, null=True)
    author = models.PositiveBigIntegerField()
    author_nick = models.CharField(max_length=50, blank=True, null=True)
    reference = models.CharField(max_length=100, help_text="Nickname for this quote")