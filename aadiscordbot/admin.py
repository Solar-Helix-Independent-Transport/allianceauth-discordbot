from django.contrib import admin

from .models import Servers, Channels, ReactionRoleBinding, ReactionRoleMessage

from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)


@admin.register(Servers)
class ServersAdmin(admin.ModelAdmin):
    list_display = ('server', 'name')
    ordering = ('name',)

    search_fields = ('name',)


@admin.register(Channels)
class ChannelsAdmin(admin.ModelAdmin):
    list_display = ('server', 'channel', 'name', 'server_name')
    ordering = ('name',)

    search_fields = ('name', 'server_name',)

    @staticmethod
    def server_name(obj):
        try:
            return obj.server.name
        except Exception as e:
            logger.error(e)


admin.site.register(ReactionRoleMessage)
admin.site.register(ReactionRoleBinding)
