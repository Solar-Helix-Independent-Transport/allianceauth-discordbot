import logging

import django
import django.db
from django.conf import settings
from celery import shared_task

logger = logging.getLogger(__name__)

## Note these Tasks do not DO anything. They can simply be called by AA to add the tasks to our Queue of choice to be consumed by bot.queueconsumer

@shared_task
def send_channel_message(channel_id, message_content, embed=False):
    ## Queue a message to a Discord Channel
    logger.debug("Queueing a Message to Channel {}".format(channel_id))
    return

@shared_task
def send_direct_message(user_id, message_content):
    ## Queue a Private Message to a specific user
    logger.debug("Queueing a Message to User {}".format(user_id))
    return