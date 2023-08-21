import json
import os
import shutil
from enum import Enum
from pathlib import Path
from typing import Type, TypeVar

from myning.objects.object import Object

T = TypeVar("T", bound=Object)


class Subfolders(str, Enum):
    ITEMS = "items"
    ENTITIES = "entities"


class FileManager:
    NEVER_DELETE = ["stats.json", "settings.json"]

    @classmethod
    def setup(cls):
        if not Path(".data").is_dir():
            os.mkdir(".data")
        if not Path(".data/items").is_dir():
            os.mkdir(".data/items")
        if not Path(".data/entities").is_dir():
            os.mkdir(".data/entities")

    @classmethod
    def multi_save(cls, *items):
        for item in items:
            cls.save(item)

    @staticmethod
    def save(item):
        path = f".data/{item.file_name}.json"
        with open(path, "w") as f:
            json.dump(item.to_dict(), f, indent=2)

    @staticmethod
    def load(type: Type[T], file_name=None, subfolder="") -> T | None:
        if subfolder:
            file_name = f".data/{subfolder}/{file_name}.json"
        else:
            file_name = f".data/{file_name}.json"
        if not Path(file_name).is_file():
            return None
        if os.path.getsize(file_name) == 0:
            return type()
        with open(file_name) as f:
            return type.from_dict(json.load(f))

    @staticmethod
    def delete(item):
        path = f".data/{item.file_name}.json"
        if Path(path).is_file():
            os.remove(path)

    @classmethod
    def multi_delete(cls, *items):
        for item in items:
            cls.delete(item)

    @staticmethod
    def reset_game():
        # Items
        for path in Path(".data/items").iterdir():
            os.remove(path)

        # Entities
        for path in Path(".data/entities").iterdir():
            os.remove(path)

        # Game
        for path in Path(".data").iterdir():
            if path.is_file() and path.name not in FileManager.NEVER_DELETE:
                os.remove(path)

    @staticmethod
    def backup_game():
        backup_dir = ".data.bak"
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
        shutil.copytree(".data", backup_dir)
