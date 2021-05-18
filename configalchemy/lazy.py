import copy
from collections import deque
from contextvars import ContextVar
from threading import Lock
from typing import TypeVar, Callable, Generic, Deque

__all__ = ["local", "lazy", "proxy", "reset_lazy", "Pool"]

LazyLoadType = TypeVar("LazyLoadType")

_sentry = object()


class BaseProxy:
    def __init__(self, obj: Callable[..., LazyLoadType], args, kwargs):
        object.__setattr__(self, "__obj__", obj)
        object.__setattr__(self, "__args__", args)
        object.__setattr__(self, "__kwargs__", kwargs)

    def __get_current_object__(self):
        raise NotImplemented

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

    async def __anext__(self):
        return await self.__get_current_object__().__anext__()

    async def __aenter__(self):
        return await self.__get_current_object__().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.__get_current_object__().__aexit__(exc_type, exc_val, exc_tb)

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
    __aiter__ = lambda x: x.__get_current_object__().__aiter__()
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


class LocalLazyObject(BaseProxy):
    def __init__(self, obj: Callable[..., LazyLoadType], args, kwargs):
        super().__init__(obj, args, kwargs)
        object.__setattr__(self, "__context_var__", ContextVar("LocalLazyObject"))

    def __get_current_object__(self):
        # evaluated once on thread access
        context_var = object.__getattribute__(self, "__context_var__")
        o = context_var.get(_sentry)
        if o is _sentry:
            o = self.__obj__(*self.__args__, **self.__kwargs__)
            context_var.set(o)
        return o


class LazyObject(BaseProxy):
    def __init__(self, obj: Callable[..., LazyLoadType], args, kwargs):
        super().__init__(obj, args, kwargs)
        object.__setattr__(self, "__attr__", _sentry)
        object.__setattr__(self, "__lock__", Lock())

    def __get_current_object__(self):
        # evaluated once on first access
        if self.__attr__ is _sentry:
            with self.__lock__:
                if self.__attr__ is _sentry:
                    object.__setattr__(
                        self,
                        "__attr__",
                        self.__obj__(*self.__args__, **self.__kwargs__),
                    )
                else:
                    return self.__attr__
        return self.__attr__


class ProxyObject(BaseProxy):
    def __get_current_object__(self):
        # evaluated on every access
        return self.__obj__(*self.__args__, **self.__kwargs__)


class PoolObject(BaseProxy):
    def __init__(self, obj: Callable[..., LazyLoadType], args, kwargs):
        super().__init__(obj, args, kwargs)
        object.__setattr__(self, "__attr__", _sentry)

    def __get_current_object__(self):
        if self.__attr__ is _sentry:
            object.__setattr__(
                self, "__attr__", self.__obj__(*self.__args__, **self.__kwargs__)
            )
        return self.__attr__


class Pool(Generic[LazyLoadType]):
    def __init__(self, obj: Callable[..., LazyLoadType], *args, **kwargs):
        self._obj = obj
        self._args = args
        self._kwargs = kwargs
        self._pool: Deque[LazyLoadType] = deque()
        self._current_active: ContextVar[LazyLoadType] = ContextVar("PoolCurrentActive")

    def _new(self) -> LazyLoadType:
        return PoolObject(self._obj, self._args, self._kwargs)  # type: ignore

    def __enter__(self) -> LazyLoadType:
        try:
            current = self._pool.pop()
        except IndexError:
            current = self._new()
        self._current_active.set(current)
        return current

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._pool.append(self._current_active.get())


def lazy(obj: Callable[..., LazyLoadType], *args, **kwargs) -> LazyLoadType:
    return LazyObject(obj, args, kwargs)  # type: ignore


def proxy(obj: Callable[..., LazyLoadType], *args, **kwargs) -> LazyLoadType:
    return ProxyObject(obj, args, kwargs)  # type: ignore


def local(obj: Callable[..., LazyLoadType], *args, **kwargs) -> LazyLoadType:
    return LocalLazyObject(obj, args, kwargs)  # type: ignore


def reset_lazy(obj):
    object.__setattr__(obj, "__attr__", _sentry)
    return obj
