import logging

import django
import django.db
from django.conf import settings
from django.contrib.auth.models import User
from celery import shared_task

logger = logging.getLogger(__name__)

## Note these Tasks do not DO anything. They can simply be called by AA to add the tasks to our Queue of choice to be consumed by bot.queueconsumer

@shared_task
def send_channel_message_by_discord_id(channel_id, message_content, embed=False):
    # Queue a message to a Discord Channel
    raise Exception("This function should be called asynchronously. Failed to queue a message to Channel {}".format(channel_id))

@shared_task
def send_direct_message_by_discord_id(discord_user_id, message_content):
    # Queue a Private Message to a specific user
    raise Exception("This function should be called asynchronously. Failed to queue a message to User {}".format(discord_user_id))

@shared_task
def send_direct_message_by_user_id(user_pk, message_content):
    # Queue a Private Message to a specific user
    raise Exception("This function should be called asynchronously. Failed to queue a message to User {}".format(user_pk))