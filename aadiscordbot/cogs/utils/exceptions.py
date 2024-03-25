from typing import Any, List

from discord.ext.commands.errors import CheckFailure

from aadiscordbot.app_settings import get_site_url


class NotAuthenticated(CheckFailure):
    """
    Custom Exception to handle any users not Authenticated with AA
    """

    def __init__(self, *args: Any) -> None:

        message = f"You must be an Authenticated user to run this command {get_site_url()}"
        super().__init__(message, *args)


class NotManaged(CheckFailure):
    """
        Custom Exception to handle any guild not managed by AA
    """

    def __init__(self, *args: Any, dm: bool = False) -> None:
        message = f"Command must be used in a guild managed by {get_site_url()}"
        super().__init__(message, *args)
