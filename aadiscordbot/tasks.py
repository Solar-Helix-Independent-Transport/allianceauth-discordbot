import logging

from celery import shared_task
from discord import Embed

import django
import django.db
from django.conf import settings
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


def send_message(message="", channel_id: int = None, user_id: int = None, user: User = None, user_pk: User = None, embed: Embed = None, countdown: int = 0):
    ''' Helper function to queue discord messages from the bot

        :param message: (optional) The text to send (default "").
        :param channel_id: (optional) the discord channel_id to send a message to.
        :param user_id: (optional) the discord user_id to send a message to as a DM.
        :param user: (optional) the Auth User Model to send a message as a DM.
        :param user_pk: (optional) the Auth Users PK to send a message as a DM.
        :param embed: (optional) the embed to send.
        :param countdown: (optional) seconds to delay the message send.
    '''
    if embed:
        embed = embed.to_dict()

    if channel_id:
        send_channel_message_by_discord_id.apply_async(
            args=[channel_id, message],
            kwargs={"embed": embed},
            countdown=countdown)

    if user_id:
        send_direct_message_by_discord_id.apply_async(
            args=[user_id, message],
            kwargs={"embed": embed},
            countdown=countdown)

    if user:
        pk = user.pk
        send_direct_message_by_user_id.apply_async(
            args=[pk, message],
            kwargs={"embed": embed},
            countdown=countdown)
    elif user_pk:
        send_direct_message_by_user_id.apply_async(
            args=[user_pk, message],
            kwargs={"embed": embed},
            countdown=countdown)

# Note these Tasks do not DO anything. They can simply be called by AA to add the tasks to our Queue of choice to be consumed by bot.queueconsumer


@shared_task
def send_channel_message_by_discord_id(channel_id, message_content, embed=False):
    # Queue a message to a Discord Channel
    raise Exception(
        f"This function should be called asynchronously. Failed to queue a message to Channel {channel_id}")


@shared_task
def send_channel_message(channel_id, message_content, embed=False):
    # DEPRECATED shim to queue a message to a Discord Channel
    raise Exception(
        f"This function should be called asynchronously. Failed to queue a message to Channel {channel_id}. Warning! This function is deprecated.")


@shared_task
def send_direct_message_by_discord_id(discord_user_id, message_content, embed=False):
    # Queue a Private Message to a specific user
    raise Exception(
        f"This function should be called asynchronously. Failed to queue a message to User {discord_user_id}")


@shared_task
def send_direct_message(user_id, message_content, embed=False):
    # DEPRECATED shim to queue a Private Message to a specific user
    raise Exception(
        f"This function should be called asynchronously. Failed to queue a message to User {discord_user_id}. Warning! This function is deprecated.")


@shared_task
def send_direct_message_by_user_id(user_pk, message_content, embed=False):
    # Queue a Private Message to a specific user
    raise Exception(
        f"This function should be called asynchronously. Failed to queue a message to User {user_pk}")
