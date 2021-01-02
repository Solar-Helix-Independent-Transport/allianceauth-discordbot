#!/usr/bin/env python
import os
import sys
import asyncio
import contextlib
import logging

from .bot import AuthBot


def run_bot():
    loop = asyncio.get_event_loop()
    log = logging.getLogger()

    bot = AuthBot()
    bot.run()
