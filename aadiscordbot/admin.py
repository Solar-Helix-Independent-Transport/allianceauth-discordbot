from django.contrib import admin

from .models import *

from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)

@admin.register(Servers)
class ServersAdmin(admin.ModelAdmin):
    list_display = ('server_id', 'server_name')
    ordering = ('server_id',)

    search_fields = ('server_name',)

@admin.register(Channels)
class ChannelsAdmin(admin.ModelAdmin):
    list_display = ('server_name', 'channel_id', 'channel_name')
    ordering = ('channel_name',)

    search_fields = ('channel_name',)

    @staticmethod
    def server_name(obj):
        try:
            return obj.server_name
        except Exception as e:
            logger.error(e)