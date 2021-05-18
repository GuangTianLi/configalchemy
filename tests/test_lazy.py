import asyncio
import copy
import time
import unittest
from concurrent.futures.thread import ThreadPoolExecutor
from functools import wraps
from typing import Optional
from unittest.mock import MagicMock

from configalchemy.lazy import lazy, proxy, reset_lazy, local, Pool


def async_test(func):
    @wraps(func)
    def wrapped(self):
        async def _():
            await func(self)

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(_())
        finally:
            loop.close()

    return wrapped


class LazyTestCase(unittest.TestCase):
    def test_lazy_load(self):
        data = {}
        lazy_data = lazy(lambda: data)
        lazy_data["test"] = 1
        self.assertEqual(dir(data), dir(lazy_data))
        self.assertEqual(repr(data), repr(lazy_data))
        self.assertEqual(repr(data), repr(lazy_data))
        self.assertEqual(bool(data), bool(lazy_data))
        del lazy_data["test"]
        self.assertNotIn("test", lazy_data)
        with self.assertRaises(AttributeError):
            lazy_data.attr

    def test_lazy_load_load_once(self):
        call_mock = MagicMock()

        def get() -> int:
            time.sleep(0.1)
            call_mock()
            return 1

        number = lazy(get)

        def task(num):
            self.assertEqual(num + 1, number + num)

        with ThreadPoolExecutor(max_workers=4) as worker:
            for _ in worker.map(task, range(4)):
                _

        self.assertEqual(1, call_mock.call_count)

    def test_local(self):
        call_mock = MagicMock()

        def get() -> int:
            time.sleep(0.1)
            call_mock()
            return 1

        number = local(get)

        def task(num):
            self.assertEqual(num + 1, number + num)

        with ThreadPoolExecutor(max_workers=4) as worker:
            for _ in worker.map(task, range(4)):
                pass

        self.assertEqual(4, call_mock.call_count)

    def test_reset_lazy(self):
        call_mock = MagicMock()

        def get() -> int:
            call_mock()
            return 1

        number = lazy(get)

        self.assertEqual(1 + 1, number + 1)
        self.assertEqual(1, call_mock.call_count)
        reset_lazy(number)
        self.assertEqual(1 + 1, number + 1)
        self.assertEqual(2, call_mock.call_count)

    def test_lazy_none(self):
        call_mock = MagicMock()

        def option() -> Optional[int]:
            call_mock()
            return None

        op = lazy(option)

        self.assertFalse(bool(op))
        self.assertFalse(bool(op))
        self.assertFalse(bool(op))
        self.assertEqual(1, call_mock.call_count)

    def test_lazy_load_operations_math(self):
        call_mock = MagicMock()

        def get() -> int:
            call_mock()
            return 2

        number = lazy(get)

        self.assertEqual(2, number)
        self.assertNotEqual(3, number)

        self.assertEqual(3, number + 1)
        self.assertEqual(3, 1 + number)

        self.assertEqual(-1, 1 - number)
        self.assertEqual(1, number - 1)

        self.assertEqual(2, number * 1)
        self.assertEqual(2, 1 * number)

        self.assertEqual(2, number / 1)
        self.assertEqual(0.5, 1.0 / number)

        self.assertEqual(2.0, number // 1)
        self.assertEqual(0.0, 1.0 // number)

        self.assertEqual(0, number % 2)
        self.assertEqual(0, 2 % number)

    def test_lazy_load_copy(self):
        class Foo:
            def __copy__(self):
                return self

            def __deepcopy__(self, memo):
                return self

        foo = Foo()
        lazy_foo = lazy(lambda: foo)
        foo.a = 1
        self.assertEqual(foo.__dict__, lazy_foo.__dict__)
        self.assertIs(foo, copy.copy(lazy_foo))
        self.assertIs(foo, copy.deepcopy(lazy_foo))

    def test_proxy_operations_math(self):
        call_mock = MagicMock()

        def get() -> int:
            call_mock()
            return 2

        number = proxy(get)

        self.assertEqual(2, number)
        self.assertNotEqual(3, number)

        self.assertEqual(3, number + 1)
        self.assertEqual(3, 1 + number)

        self.assertEqual(-1, 1 - number)
        self.assertEqual(1, number - 1)

        self.assertEqual(2, number * 1)
        self.assertEqual(2, 1 * number)

        self.assertEqual(2, number / 1)
        self.assertEqual(0.5, 1.0 / number)

        self.assertEqual(2.0, number // 1)
        self.assertEqual(0.0, 1.0 // number)

        self.assertEqual(0, number % 2)
        self.assertEqual(0, 2 % number)

        self.assertEqual(14, call_mock.call_count)

    @async_test
    async def test_coroutine(self):
        aenter = MagicMock()
        aexit = MagicMock()

        class Reader:
            readline = iter([b"test", b""])

            def __aiter__(self):
                return self

            async def __anext__(self):
                val = next(self.readline)
                if val == b"":
                    raise StopAsyncIteration
                return val

            async def __aenter__(self):
                aenter()
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                aexit()

        reader = lazy(Reader)
        self.assertEqual([b"test"], [v async for v in reader])

        async with reader:
            pass
        aenter.assert_called_once()
        aexit.assert_called_once()

    def test_pool(self):
        call_mock = MagicMock()

        def get() -> int:
            time.sleep(1)
            call_mock()
            return 1

        pool = Pool(get)

        def task(num):
            with pool as number:
                self.assertEqual(num + 1, number + num)
            with pool as number:
                self.assertEqual(num + 1, number + num)

        with ThreadPoolExecutor(max_workers=4) as worker:
            for _ in worker.map(task, range(4)):
                pass
        self.assertEqual(4, call_mock.call_count)


if __name__ == "__main__":
    unittest.main()
