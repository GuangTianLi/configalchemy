import unittest

from configalchemy import get_current_config, BaseConfig


class GlobalAPITestCase(unittest.TestCase):
    def test_get_current_config(self):
        class DefaultConfig(BaseConfig):
            TEST = "test"

        current_config = get_current_config(DefaultConfig)
        self.assertEqual("test", current_config.TEST)

        DefaultConfig().TEST = "inited"
        current_config = get_current_config(DefaultConfig)
        self.assertEqual("inited", current_config.TEST)


if __name__ == "__main__":
    unittest.main()
