import logging

import django
import django.db
from django.conf import settings
from django.contrib.auth.models import User
from celery import shared_task
from discord import Embed

logger = logging.getLogger(__name__)

def send_message(message="", channel_id : int=None, user_id : int=None, user : User=None, user_pk : User=None, embed :Embed=None):
    ''' Helper function to queue discord messages fromt the bot

        :param message: (optional) The text to send (default "").
        :param channel_id: (optional) the discord channel_id to send a message to.
        :param channel_id: (optional) the disccord user_id to send a message to as a DM.
        :param user: (optional) the Auth User Model to send a message.
        :param user_pk: (optional) the auth Users PK to send a message.
        :param embed: (optional) the embed to send.
    '''
    if embed:
        embed = embed=embed.to_dict()

    if channel_id:
        send_channel_message_by_discord_id.delay(channel_id, message, embed=embed)

    if user_id:
        send_direct_message_by_discord_id.delay(user_id, message, embed=embed)
    
    if user:
        pk = user.pk
        send_direct_message_by_user_id.delay(pk, message, embed=embed)
    elif user_pk:
        send_direct_message_by_user_id.delay(user_pk, message, embed=embed)

## Note these Tasks do not DO anything. They can simply be called by AA to add the tasks to our Queue of choice to be consumed by bot.queueconsumer
@shared_task
def send_channel_message_by_discord_id(channel_id, message_content, embed=False):
    # Queue a message to a Discord Channel
    raise Exception("This function should be called asynchronously. Failed to queue a message to Channel {}".format(channel_id))

@shared_task
def send_channel_message(channel_id, message_content, embed=False):
    # DEPRECATED shim to queue a message to a Discord Channel
    raise Exception("This function should be called asynchronously. Failed to queue a message to Channel {}. Warning! This function is deprecated.".format(channel_id))

@shared_task
def send_direct_message_by_discord_id(discord_user_id, message_content, embed=False):
    # Queue a Private Message to a specific user
    raise Exception("This function should be called asynchronously. Failed to queue a message to User {}".format(discord_user_id))

@shared_task
def send_direct_message(user_id, message_content, embed=False):
    # DEPRECATED shim to queue a Private Message to a specific user
    raise Exception("This function should be called asynchronously. Failed to queue a message to User {}. Warning! This function is deprecated.".format(discord_user_id))

@shared_task
def send_direct_message_by_user_id(user_pk, message_content, embed=False):
    # Queue a Private Message to a specific user
    raise Exception("This function should be called asynchronously. Failed to queue a message to User {}".format(user_pk))