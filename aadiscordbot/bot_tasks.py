import logging
from discord.utils import get
from discord.ext import tasks

logger = logging.getLogger(__name__)

@tasks.loop()
async def run_tasks(bot):
    if len(bot.tasks) > 0:
        task, args = bot.tasks.pop(0)
        await task(bot, args)
    else:
        run_tasks.stop()

async def send_channel_message(bot, args):
    logger.debug("I am running a Send Channel Message Task")
    channel_id = int(args[0])
    await bot.get_channel(channel_id).send(args[1].strip("'"))

async def send_direct_message(bot, args):
    logger.debug("i am running a Direct Message Task")
    user_id = int(args[0])
    
    channel = await bot.get_user(user_id).create_dm()
    await channel.send(args[1].strip("'"))
