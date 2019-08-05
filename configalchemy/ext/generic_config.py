from typing import TypeVar, Callable, Any

T = TypeVar("T")


class GenericConfigMixin:
    def __init__(self, value: T, *, typecast: Callable[[Any], Any]):
        super().__init__(value)  # type: ignore
        self.__typecast__ = typecast

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
