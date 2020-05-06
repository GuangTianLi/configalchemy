import copy
from threading import Lock
from typing import TypeVar, Callable

LazyLoadType = TypeVar("LazyLoadType")


class LazyObject:
    __slots__ = ("__obj__", "__kwargs__", "__attr__", "__lock__", "__dict__")

    def __init__(self, obj: Callable[..., LazyLoadType], args, kwargs):
        object.__setattr__(self, "__obj__", obj)
        object.__setattr__(self, "__args__", args)
        object.__setattr__(self, "__kwargs__", kwargs)
        object.__setattr__(self, "__attr__", None)
        object.__setattr__(self, "__lock__", Lock())

    def __get_current_object__(self):
        # evaluated once on first access
        if self.__attr__ is None:
            with self.__lock__:
                if self.__attr__ is None:
                    object.__setattr__(
                        self,
                        "__attr__",
                        self.__obj__(*self.__args__, **self.__kwargs__),
                    )
                else:
                    return self.__attr__
        return self.__attr__

    def __getattr__(self, item):
        return getattr(self.__get_current_object__(), item)

    @property
    def __dict__(self):
        try:
            return self.__get_current_object__().__dict__
        except RuntimeError:
            raise AttributeError("__dict__")

    def __repr__(self):
        obj = self.__get_current_object__()
        return repr(obj)

    def __bool__(self):
        return bool(self.__get_current_object__())

    def __dir__(self):
        return dir(self.__get_current_object__())

    def __setitem__(self, key, value):
        self.__get_current_object__()[key] = value

    def __delitem__(self, key):
        del self.__get_current_object__()[key]

    __setattr__ = lambda x, n, v: setattr(
        x.__get_current_object__(), n, v  # type: ignore
    )
    __delattr__ = lambda x, n: delattr(x.__get_current_object__(), n)  # type: ignore
    __str__ = lambda x: str(x.__get_current_object__())  # type: ignore
    __lt__ = lambda x, o: x.__get_current_object__() < o
    __le__ = lambda x, o: x.__get_current_object__() <= o
    __eq__ = lambda x, o: x.__get_current_object__() == o  # type: ignore
    __ne__ = lambda x, o: x.__get_current_object__() != o  # type: ignore
    __gt__ = lambda x, o: x.__get_current_object__() > o
    __ge__ = lambda x, o: x.__get_current_object__() >= o
    __hash__ = lambda x: hash(x.__get_current_object__())  # type: ignore
    __call__ = lambda x, *a, **kw: x.__get_current_object__()(*a, **kw)
    __len__ = lambda x: len(x.__get_current_object__())
    __getitem__ = lambda x, i: x.__get_current_object__()[i]
    __iter__ = lambda x: iter(x.__get_current_object__())
    __contains__ = lambda x, i: i in x.__get_current_object__()
    __add__ = lambda x, o: x.__get_current_object__() + o
    __sub__ = lambda x, o: x.__get_current_object__() - o
    __mul__ = lambda x, o: x.__get_current_object__() * o
    __floordiv__ = lambda x, o: x.__get_current_object__() // o
    __mod__ = lambda x, o: x.__get_current_object__() % o
    __divmod__ = lambda x, o: x.__get_current_object__().__divmod__(o)
    __pow__ = lambda x, o: x.__get_current_object__() ** o
    __lshift__ = lambda x, o: x.__get_current_object__() << o
    __rshift__ = lambda x, o: x.__get_current_object__() >> o
    __and__ = lambda x, o: x.__get_current_object__() & o
    __xor__ = lambda x, o: x.__get_current_object__() ^ o
    __or__ = lambda x, o: x.__get_current_object__() | o
    __div__ = lambda x, o: x.__get_current_object__().__div__(o)
    __truediv__ = lambda x, o: x.__get_current_object__().__truediv__(o)
    __neg__ = lambda x: -(x.__get_current_object__())
    __pos__ = lambda x: +(x.__get_current_object__())
    __abs__ = lambda x: abs(x.__get_current_object__())
    __invert__ = lambda x: ~(x.__get_current_object__())
    __complex__ = lambda x: complex(x.__get_current_object__())
    __int__ = lambda x: int(x.__get_current_object__())
    __float__ = lambda x: float(x.__get_current_object__())
    __oct__ = lambda x: oct(x.__get_current_object__())
    __hex__ = lambda x: hex(x.__get_current_object__())
    __index__ = lambda x: x.__get_current_object__().__index__()
    __coerce__ = lambda x, o: x.__get_current_object__().__coerce__(x, o)
    __enter__ = lambda x: x.__get_current_object__().__enter__()
    __exit__ = lambda x, *a, **kw: x.__get_current_object__().__exit__(*a, **kw)
    __radd__ = lambda x, o: o + x.__get_current_object__()
    __rsub__ = lambda x, o: o - x.__get_current_object__()
    __rmul__ = lambda x, o: o * x.__get_current_object__()
    __rdiv__ = lambda x, o: o / x.__get_current_object__()
    __rtruediv__ = __rdiv__
    __rfloordiv__ = lambda x, o: o // x.__get_current_object__()
    __rmod__ = lambda x, o: o % x.__get_current_object__()
    __rdivmod__ = lambda x, o: x.__get_current_object__().__rdivmod__(o)
    __copy__ = lambda x: copy.copy(x.__get_current_object__())
    __deepcopy__ = lambda x, memo: copy.deepcopy(x.__get_current_object__(), memo)


class ProxyLazyObject(LazyObject):
    def __get_current_object__(self):
        # evaluated on every access
        return self.__obj__(*self.__args__, **self.__kwargs__)


def lazy(obj: Callable[..., LazyLoadType], *args, **kwargs) -> LazyLoadType:
    return LazyObject(obj, args, kwargs)  # type: ignore


def proxy(obj: Callable[..., LazyLoadType], *args, **kwargs) -> LazyLoadType:
    return ProxyLazyObject(obj, args, kwargs)  # type: ignore
