from aadiscordbot import launcher
import asyncio
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myauth.settings.local")
# shakes head in shame... this import must be under that ^


def main():
    loop = asyncio.get_event_loop()
    launcher.run_bot()


if __name__ == "__main__":
    main()
