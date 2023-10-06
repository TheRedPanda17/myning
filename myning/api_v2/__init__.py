from typing import Literal

import aiohttp

from myning.objects.singleton import Singleton
from myning.utilities.file_manager import FileManager


class MyningClient(metaclass=Singleton):
    @classmethod
    def initialize(cls):
        client = FileManager.load(MyningClient, cls.file_name)
        if not client:
            client = cls()
        cls._instance = client

    @classmethod
    @property
    def file_name(cls):
        return "login"

    def __init__(self, username=None, password=None, user_id=None) -> None:
        self.base_url = "http://129.146.87.150:8080"
        self.headers = {"MYNING-CLIENT": "tui-game"}
        self.username = username
        self.password = password
        self.user_id = user_id

    def to_dict(self):
        return {"username": self.username, "password": self.password, "user_id": self.user_id}

    @classmethod
    def from_dict(cls, dict: dict):
        if not dict:
            return MyningClient()
        return MyningClient(dict["username"], dict["password"], dict["user_id"])

    @property
    def auth(self) -> aiohttp.BasicAuth | None:
        if self.username or self.password:
            return aiohttp.BasicAuth(login=self.username, password=self.password)

    def set_username(self, username):
        self.username = username

    def set_password(self, password):
        self.password = password

    async def fetch(
        self,
        path: str,
        method: Literal["GET", "POST", "PATCH"] = "GET",
        json: dict = None,
        auth: aiohttp.BasicAuth = None,
    ):
        url = f"{self.base_url}{path}"

        if not auth:
            auth = self.auth

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                headers=self.headers,
                auth=auth,
                json=json,
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def sign_in(self, username: str, password: str):
        user = await self.fetch(
            f"/auth", "GET", auth=aiohttp.BasicAuth(login=username, password=password)
        )
        if user:
            self.username = username
            self.password = password
            self.user_id = user["id"]
        return user

    async def create_account(self, username: str, password: str):
        user = await self.fetch(f"/users", "POST", {"name": username, "password": password})
        if user:
            self.username = self.username
            self.password = self.password
        return user
