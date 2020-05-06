import copy
import time
import unittest
from concurrent.futures.thread import ThreadPoolExecutor
from unittest.mock import MagicMock

from configalchemy.lazy import lazy, proxy


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
            self.assertEqual(num + 1, number + 1)

        with ThreadPoolExecutor(max_workers=4) as worker:
            worker.map(task, range(4))

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


if __name__ == "__main__":
    unittest.main()
