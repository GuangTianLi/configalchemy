import unittest

from configalchemy import get_current_config, BaseConfig


class GlobalAPITestCase(unittest.TestCase):
    def test_get_current_config(self):
        class DefaultConfig(BaseConfig):
            TEST = "test"

        with self.assertRaises(RuntimeError):
            get_current_config(DefaultConfig)

        with self.assertRaises(RuntimeError):
            DefaultConfig()
            get_current_config(DefaultConfig)
        config = DefaultConfig()
        config.TEST = "inited"
        current_config = get_current_config(DefaultConfig)
        self.assertEqual("inited", current_config.TEST)


if __name__ == "__main__":
    unittest.main()
