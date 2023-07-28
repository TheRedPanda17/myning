from abc import abstractmethod
from typing import Type, TypeVar

T = TypeVar("T", bound="Object")


class Object:
    @property
    @abstractmethod
    def file_name(self) -> str:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls: Type[T], d: dict) -> T:
        pass
