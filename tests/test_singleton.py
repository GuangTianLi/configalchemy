import unittest

from configalchemy import BaseConfig, SingletonMetaClass


class GlobalAPITestCase(unittest.TestCase):
    def test_get_current_config(self):
        class DefaultConfig(BaseConfig, metaclass=SingletonMetaClass):
            TEST = "test"

        with self.assertRaises(RuntimeError):
            DefaultConfig.instance()

        config = DefaultConfig()
        config.TEST = "inited"
        current_config = DefaultConfig.instance()
        self.assertEqual("inited", current_config.TEST)


if __name__ == "__main__":
    unittest.main()
