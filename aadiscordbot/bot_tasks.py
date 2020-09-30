import logging
from discord.utils import get

logger = logging.getLogger(__name__)

async def send_channel_message(bot, args):
    logger.debug("I am running a Send Channel Message Task")
    channel_id = int(args[0])
    await bot.get_channel(channel_id).send(args[1])

async def send_direct_message(bot, args):
    logger.debug("i am running a Direct Message Task")
    user_id = int(args[0])
    
    channel = await bot.get_user(user_id).create_dm()
    await channel.send(args[1].strip("'"))
