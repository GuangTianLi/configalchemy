import unittest

from configalchemy import BaseConfig
from configalchemy.utils import import_reference


class UtilsTestCase(unittest.TestCase):
    def test_import_reference(self):
        self.assertEqual(
            id(BaseConfig),
            id(import_reference("configalchemy.configalchemy.BaseConfig")),
        )


if __name__ == "__main__":
    unittest.main()
