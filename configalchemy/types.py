import functools
import json
from typing import Union, Type, cast, Any, TypeVar

_cleanups = []


def _tp_cache(func):
    """Internal wrapper caching __getitem__ of generic types with a fallback to
    original function for non-hashable arguments.
    """
    cached = functools.lru_cache()(func)
    _cleanups.append(cached.cache_clear)

    @functools.wraps(func)
    def inner(*args, **kwds):
        try:
            return cached(*args, **kwds)
        except TypeError:
            pass  # All real errors (not unhashable args) are raised below.
        return func(*args, **kwds)

    return inner


class GenericConfigMixin:
    def __type_check__(self, instance: Any) -> bool:
        return isinstance(instance, self.__class__)

    def __typecast__(self, value: Any) -> Any:
        raise TypeError(f"Object of type {self.__class__.__name__} can not be typecast")


JsonSerializable = Union[int, float, bool, list, dict, str]
ItemType = TypeVar("ItemType", bound=JsonSerializable)


class JsonMeta(GenericConfigMixin):
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
