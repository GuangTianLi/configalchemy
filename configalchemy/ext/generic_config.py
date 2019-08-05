from typing import TypeVar, Callable, Any

T = TypeVar("T")


class GenericConfigMixin:
    def __new__(cls, value: T, *, typecast: Callable[[Any], Any]) -> T:
        self = super().__new__(cls, value)
        self.__typecast__ = typecast
        return self

    @classmethod
    def __isinstance__(cls, value) -> bool:
        return isinstance(value, cls)


class ListConfig(GenericConfigMixin, list):
    @classmethod
    def __isinstance__(cls, value) -> bool:
        return isinstance(value, list)


class DictConfig(GenericConfigMixin, dict):
    @classmethod
    def __isinstance__(cls, value) -> bool:
        return isinstance(value, dict)
