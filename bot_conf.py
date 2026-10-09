import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myauth.settings.local")
# shakes head in shame... this import must be under that ^
from aadiscordbot import launcher  # noqa: E402


def main() -> None:
    launcher.run_bot()


if __name__ == "__main__":
    main()
