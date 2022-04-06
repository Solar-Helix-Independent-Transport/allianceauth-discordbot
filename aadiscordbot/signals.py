import pprint
from django.db.models.signals import post_save
from django.dispatch import receiver

from allianceauth.notifications.models import Notification
import inspect

from django.apps import apps


monitored_modules = ["allianceauth.notifications",
                     "allianceauth.notifications.managers"]
monitored_functions = ["notify", "notify_user"]


@receiver(post_save, sender=Notification)
def new_notification(sender, instance: Notification, created, **kwargs):
    aps = apps.get_app_configs()
    stack = inspect.stack()
    stack_lookup = range(6, 15)
    last = -1
    for i in stack_lookup:
        if (inspect.getmodule(stack[i][0]).__name__ in monitored_modules
                and stack[i][3] in monitored_functions):
            last = i
            if (inspect.getmodule(stack[i+1][0]).__name__ in monitored_modules
                    and stack[i+1][3] in monitored_functions):
                last += 1
            break
    if last > 0:
        print("Notification came from module `{}` function `{}`".format(
            inspect.getmodule(stack[last+1][0]).__package__, stack[last+1][3]))
    else:
        print("Unknown Module Ignoring filter!")
    del stack
