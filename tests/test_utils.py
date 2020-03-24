import unittest

from configalchemy import BaseConfig
from configalchemy.utils import import_reference, find_caller


class UtilsTestCase(unittest.TestCase):
    def test_import_reference(self):
        self.assertEqual(
            id(BaseConfig),
            id(import_reference("configalchemy.configalchemy.BaseConfig")),
        )

    def test_find_caller(self):
        stack_info = find_caller()
        stack_str = "stack_info = find_caller()"
        self.assertEqual(stack_str, stack_info[-len(stack_str) :])


if __name__ == "__main__":
    unittest.main()
