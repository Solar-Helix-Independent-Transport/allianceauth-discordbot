#!/usr/bin/env python
import asyncio

from .bot import AuthBot


def run_bot():

    bot = AuthBot()
    asyncio.run(bot.run())
