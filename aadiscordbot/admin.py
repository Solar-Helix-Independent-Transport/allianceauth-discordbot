from solo.admin import SingletonModelAdmin

from django.contrib import admin

from allianceauth.services.hooks import get_extension_logger

from .models import (
    AuthBotConfiguration, Channels, GoodbyeMessage, ReactionRoleBinding,
    ReactionRoleMessage, Servers, TicketGroups, WelcomeMessage,
)

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


@admin.register(AuthBotConfiguration)
class AuthBotConfigurationAdmin(SingletonModelAdmin):
    filter_horizontal = ['admin_users']


@admin.register(ReactionRoleMessage)
class RRAdmin(admin.ModelAdmin):
    list_display = ('name', 'non_auth_users')
    ordering = ('name',)

    search_fields = ('name',)


@admin.register(ReactionRoleBinding)
class RRBAdmin(admin.ModelAdmin):
    list_display = ('message_name', 'emoji_decoded', 'group')

    search_fields = ('message_name', 'emoji_decoded', 'group')

    @staticmethod
    def message_name(obj):
        try:
            return obj.message.name
        except Exception as e:
            logger.error(e)

    @staticmethod
    def emoji_decoded(ob):
        try:
            b = eval(ob.emoji_text).decode('utf-8')
        except Exception:
            b = ob.emoji_text
        return b


@admin.register(WelcomeMessage)
class WelcomeMessageAdmin(admin.ModelAdmin):
    list_display = ('guild_id', 'id', "authenticated", "unauthenticated")


@admin.register(GoodbyeMessage)
class GoodbyeMessageAdmin(admin.ModelAdmin):
    list_display = ('guild_id', 'id', "authenticated", "unauthenticated")


@admin.register(TicketGroups)
class TicketGroupAdmin(SingletonModelAdmin):
    filter_horizontal = ['groups']
