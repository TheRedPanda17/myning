import os
from base64 import b64encode
from typing import Literal

import aiohttp


# Needed once we had username and passwords
def basic_auth(username, password):
    return f'Basic {b64encode(bytes(f"{username}:{password}", "utf-8")).decode("ascii")}'


API_CONFIG = {
    "base_url": "https://myning.vercel.app/api",
    "auth": os.environ.get("API_KEY"),
}


async def fetch(url: str, method: Literal["GET", "POST", "PATCH"] = "GET", headers=None, json=None):
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, headers=headers, json=json) as response:
            response.raise_for_status()
            return await response.json()


# pylint: disable=wrong-import-position
from . import players
