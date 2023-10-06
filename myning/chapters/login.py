from myning.api_v2 import MyningClient
from myning.chapters import (
    AsyncArgs,
    DynamicArgs,
    Option,
    PickArgs,
    api_request,
    main_menu,
    tutorial,
)


from typing import TYPE_CHECKING

from myning.tui.input import LoginFormScreen

if TYPE_CHECKING:
    from myning.tui.chapter import ChapterWidget


def enter():
    options = [
        Option("Log In", login),
        Option("Sign Up", signup),
    ]

    return PickArgs(
        message="Welcome to Myning!",
        options=options,
    )


def login():
    def get_login_callback(chapter: "ChapterWidget"):
        async def screen_callback(result):
            if not result:
                return

            username, password = result
            await check_auth(chapter, username, password)

        chapter.app.push_screen(
            LoginFormScreen("Log In"),
            screen_callback,
        )

    return DynamicArgs(callback=get_login_callback)


@api_request("Signing In...", enter)
async def check_auth(chapter: "ChapterWidget", username: str, password: str):
    client = MyningClient()
    try:
        user = await client.sign_in(username, password)
    except Exception as e:
        chapter.pick(
            PickArgs(
                message=f"Error logging in: {e}",
                options=[Option("I'll try again", enter)],
            )
        )
        return

    proceed = main_menu.enter if tutorial.is_complete() else tutorial.enter
    chapter.pick(
        PickArgs(
            message=f"Welcome back, {user['name']}!",
            options=[Option("Let's get myning!", proceed)],
        )
    )


def signup():
    def get_login_callback(chapter: "ChapterWidget"):
        async def screen_callback(result):
            if not result:
                return

            username, password = result
            await create_account(chapter, username, password)

        chapter.app.push_screen(
            LoginFormScreen("Sign Up"),
            screen_callback,
        )

    return DynamicArgs(callback=get_login_callback)


@api_request("Creating Account...", enter)
async def create_account(chapter: "ChapterWidget", username: str, password: str):
    client = MyningClient()
    try:
        user = await client.create_account(username, password)
    except Exception as e:
        chapter.pick(
            PickArgs(
                message=f"Error logging in: {e}",
                options=[Option("I'll try again", enter)],
            )
        )
        return

    proceed = main_menu.enter if tutorial.is_complete() else tutorial.enter
    chapter.pick(
        PickArgs(
            message=f"Welcome, {user['name']}!",
            options=[Option("Let's get myning!", proceed)],
        )
    )
