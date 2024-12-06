import logging

from aadiscordbot.tasks import run_task_function

logger = logging.getLogger(__name__)


async def send_configuration_to_log(bot, message, commands=False):
    logger.error(f"{bot.user} {message} - (commands: {commands})")
    logger.error(f"Guilds: {len(bot.guilds)}")
    logger.error(f"Users:  {len(bot.users)}")


def run_task():
    """
from aadiscordbot.tests.task_tests import run_task
run_task()
    """
    run_task_function.delay(
        "aadiscordbot.tests.task_tests.send_configuration_to_log",
        ["TESTING a custom function!"],
        {"commands":True}
    )
