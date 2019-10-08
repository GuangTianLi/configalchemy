import functools
import json
from typing import Union, Type, cast, Any, TypeVar


def _tp_cache(func):
    """Internal wrapper caching __getitem__ of generic types with a fallback to
    original function for non-hashable arguments.
    """
    cached = functools.lru_cache()(func)

    @functools.wraps(func)
    def inner(*args, **kwds):  # pragma: no cover
        try:
            return cached(*args, **kwds)
        except TypeError:
            pass  # All real errors (not unhashable args) are raised below.
        return func(*args, **kwds)

    return inner


class GenericConfigMixin:
    @classmethod
    def __type_check__(cls, instance: Any) -> bool:
        return isinstance(instance, cls)

    @classmethod
    def __typecast__(cls, value: Any) -> Any:
        raise TypeError(f"Object of type {cls.__name__} can not be typecast")


JsonSerializable = Union[int, float, bool, list, dict, str]
ItemType = TypeVar("ItemType", bound=JsonSerializable)


class JsonMeta:
    __slots__ = ("__origin__",)

    def __init__(self, origin: Type[ItemType]):
        self.__origin__ = getattr(origin, "__origin__", origin)

    @_tp_cache
    def __getitem__(self, t: Type[ItemType]) -> Type[ItemType]:
        return cast(Type[ItemType], JsonMeta(origin=t))

    def __type_check__(self, instance: Any) -> bool:
        return isinstance(instance, self.__origin__)

    def __typecast__(self, value: Any) -> Any:
        return json.loads(value)


Json = JsonMeta(origin=dict)


class SecretStr(str):
    def __repr__(self) -> str:
        return "SecretStr('**********')"

    def __str__(self) -> str:
        return repr(self)
