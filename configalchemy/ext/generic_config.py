import json
from typing import TypeVar, Callable, Any, TYPE_CHECKING

T = TypeVar("T")


class GenericConfigMixin:
    def __init__(self, value: T, *, typecast: Callable[[Any], Any] = json.loads):
        super().__init__(value)  # type: ignore
        self.__typecast__ = typecast

    def __instancecheck__(self, value) -> bool:
        return False


class ListConfig(GenericConfigMixin, list):
    if TYPE_CHECKING:  # pragma: no cover

        def __new__(cls, value: T, typecast: Callable[[Any], Any]) -> T:
            ...

    def __instancecheck__(self, instance) -> bool:
        return isinstance(instance, list)


class DictConfig(GenericConfigMixin, dict):
    if TYPE_CHECKING:  # pragma: no cover

        def __new__(cls, value: T, typecast: Callable[[Any], Any]) -> T:
            ...

    def __instancecheck__(self, instance) -> bool:
        return isinstance(instance, dict)
