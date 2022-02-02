from . import urls
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook
from allianceauth.authentication.models import UserProfile, State
from . import app_settings
"""
class CeleryMenu(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self, 'Celery Tasks',
                              'fa fa-clock fa-fw',
                              'celeryanalytics:show_tasks',
                              navactive=['celeryanalytics:show_tasks'])

    def render(self, request):
        if request.user.is_staff:
            return MenuItemHook.render(self, request)
        return ''


@hooks.register('menu_item_hook')
def register_menu():
    return CeleryMenu()

@hooks.register('url_hook')
def register_url():
    return UrlHook(urls, 'celeryanalytics', r'^celeryanalytics/')
"""


@hooks.register('discord_cogs_hook')
def register_cogs():
    return app_settings.DISCORD_BOT_COGS
