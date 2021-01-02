import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myauth.settings.local")
import asyncio
from aadiscordbot import launcher


def main(ctx):
    loop = asyncio.get_event_loop()
    launcher.run_bot()


if __name__ == "__main__":
    main()
