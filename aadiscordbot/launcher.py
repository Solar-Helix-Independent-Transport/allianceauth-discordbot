#!/usr/bin/env python
import asyncio
import contextlib
import logging
import os
import sys

from .bot import AuthBot


def run_bot():
    loop = asyncio.get_event_loop()
    log = logging.getLogger()

    bot = AuthBot()
    bot.run()
