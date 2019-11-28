import functools
import json
from typing import Union, Type, cast, Any, TypeVar, Generic, TYPE_CHECKING, Tuple, Dict


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


T = TypeVar("T")


class DefaultTypeCast(Generic[T]):
    if TYPE_CHECKING:  # pragma: no cover
        # populated by the Generic, defined here to help IDEs only
        __orig_bases__: Tuple[Any, ...]

    @classmethod
    def __type_check__(cls, instance: Any) -> bool:
        return isinstance(instance, cls.__orig_bases__[0].__args__[0])

    @classmethod
    def __typecast__(cls, value: Any) -> T:
        raise TypeError(f"Object of type {cls.__name__} can not be typecast")


BOOL_STRINGS = {"true", "1", "yes", "y"}


class Boolean(DefaultTypeCast[bool]):
    @classmethod
    def __typecast__(self, value: Any) -> bool:
        if isinstance(value, str):
            return value.lower() in BOOL_STRINGS
        else:
            return bool(value)


DEFAULT_TYPE_CAST: Dict[Type, Type[DefaultTypeCast]] = {bool: Boolean}
