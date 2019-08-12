import json
import os
import unittest
from unittest.mock import Mock

from configalchemy import BaseConfig, ConfigType
from configalchemy.ext.generic_config import ListConfig, DictConfig


class GenericConfigTestCase(unittest.TestCase):
    def test_ListConfig_typecast(self):
        typecast = Mock(return_value=["test"])

        class DefaultConfig(BaseConfig):
            CONFIGALCHEMY_ENABLE_FUNCTION = True
            CONFIGALCHEMY_ENV_PREFIX = "TEST_"
            TEST_LIST = ListConfig(["str"], typecast=typecast)

            def sync_function(self) -> ConfigType:
                return {"TEST_LIST": ["FUNCTION"]}

        os.environ.setdefault("TEST_TEST_LIST", json.dumps(["test"]))
        config = DefaultConfig()

        typecast.assert_called_with(json.dumps(["test"]))
        typecast.assert_called_once()
        self.assertEqual(config.TEST_LIST, ["test"])

    def test_DictConfig_typecast(self):
        typecast = Mock(return_value={"name": "test"})

        class DefaultConfig(BaseConfig):
            CONFIGALCHEMY_ENABLE_FUNCTION = True
            CONFIGALCHEMY_ENV_PREFIX = "TEST_"
            TEST_DICT = DictConfig({"name": "default"}, typecast=typecast)

            def sync_function(self) -> ConfigType:
                return {"TEST_DICT": {"name": "function"}}

        os.environ.setdefault("TEST_TEST_DICT", json.dumps({"name": "test"}))
        config = DefaultConfig()

        typecast.assert_called_with(json.dumps({"name": "test"}))
        typecast.assert_called_once()
        self.assertEqual(config.TEST_DICT["name"], "test")


if __name__ == "__main__":
    unittest.main()
