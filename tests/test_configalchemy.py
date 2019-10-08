"""Tests for `configalchemy` package."""
import json
import os
import unittest

from configalchemy import BaseConfig, ConfigType


class ConfigalchemyTestCase(unittest.TestCase):
    """Tests for `configalchemy` package."""

    json_file = "test.json"

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    @classmethod
    def setUpClass(cls) -> None:
        with open(cls.json_file, "w") as fp:
            json.dump({"JSON_TEST": "JSON_TEST"}, fp)

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(cls.json_file)

    def test_default_config_init_from_object(self):
        class DefaultConfig(BaseConfig):
            TEST = "test"

        config = DefaultConfig()

        self.assertEqual("test", config["TEST"])
        self.assertEqual("test", config.TEST)
        with self.assertRaises(KeyError):
            _ = config["NOT_EXIST"]

        def test_unpack(**kw):
            self.assertEqual(config, kw)

        test_unpack(**config)
        self.assertEqual("NOT_EXIST", config.get("NOT_EXIST", "NOT_EXIST"))

        self.assertTrue(config)
        self.assertTrue("TEST" in config)
        self.assertEqual(len(config), len(list(iter(config))))

        config.update(dict(TEST="update"))
        config.update(dict(TEST="updated"))
        self.assertEqual("updated", config["TEST"])
        self.assertEqual("updated", config.TEST)
        del config["TEST"]
        del config["TEST"]
        self.assertEqual("test", config.TEST)
        self.assertEqual("test", DefaultConfig.TEST)
        self.assertEqual("test", config["TEST"])
        self.assertEqual("test", json.loads(config.json())["TEST"])
        self.assertEqual(str(config), str(json.loads(config.json())))

    def test_default_config_update_from_json(self):
        class DefaultConfig(BaseConfig):
            CONFIGALCHEMY_CONFIG_FILE = self.json_file

            JSON_TEST = "default"

        config = DefaultConfig()

        self.assertEqual("JSON_TEST", config["JSON_TEST"])
        self.assertEqual("JSON_TEST", config.JSON_TEST)

    def test_config_file_not_exist(self):
        class DefaultConfig(BaseConfig):
            CONFIGALCHEMY_ENV_PREFIX = "CONFIGALCHEMY_"
            CONFIGALCHEMY_CONFIG_FILE = "not.exist"

        with self.assertRaises(IOError):
            DefaultConfig()

        os.environ.setdefault("CONFIGALCHEMY_CONFIGALCHEMY_LOAD_FILE_SILENT", "True")
        DefaultConfig()

    def test_config_with_env(self):
        os.environ["test_TEST"] = "changed"

        class DefaultConfig(BaseConfig):
            CONFIGALCHEMY_ENV_PREFIX = "test_"
            TEST = "default"

        config = DefaultConfig()
        self.assertEqual("changed", config["TEST"])
        self.assertEqual("changed", config.TEST)

    def test_update_config_from_function(self):
        class DefaultConfig(BaseConfig):
            CONFIGALCHEMY_ENABLE_FUNCTION = True
            TEST = "default"

            def sync_function(self) -> ConfigType:
                return {"TEST": "changed"}

        config = DefaultConfig()
        self.assertEqual("changed", config["TEST"])
        self.assertEqual("changed", config.TEST)

    def test_async_update_config_from_function(self):
        class DefaultConfig(BaseConfig):
            CONFIGALCHEMY_ENABLE_FUNCTION = True
            TEST = "default"

            async def async_function(self) -> ConfigType:
                return {"TEST": "changed"}

        config = DefaultConfig()
        self.assertEqual("changed", config["TEST"])
        self.assertEqual("changed", config.TEST)

    def test_config_priority(self):
        os.environ["test_FOURTH"] = "4"
        current_json_file = "test_priority.json"

        with open(current_json_file, "w") as fp:
            json.dump({"THIRD": "3", "FOURTH": "3"}, fp)

        class DefaultConfig(BaseConfig):
            # env
            CONFIGALCHEMY_ENV_PREFIX = "test_"
            # file
            CONFIGALCHEMY_CONFIG_FILE = current_json_file
            CONFIGALCHEMY_ENABLE_FUNCTION = True

            FIRST = 1
            SECOND = "1"
            THIRD = "1"
            FOURTH = 1

            def sync_function(self) -> ConfigType:
                return {"SECOND": "2", "FOURTH": "2"}

            async def async_function(self) -> ConfigType:
                return {"THIRD": 2, "FOURTH": 2}

        config = DefaultConfig()
        os.remove(current_json_file)

        self.assertEqual(1, config["FIRST"])
        self.assertEqual("2", config["SECOND"])
        self.assertEqual("3", config["THIRD"])
        self.assertEqual(4, config["FOURTH"])
        config.access_config_from_function(config.CONFIGALCHEMY_FUNCTION_VALUE_PRIORITY)
        self.assertEqual(4, config["FOURTH"])

    def test_multiple_inheritance(self):
        class AConfig(BaseConfig):
            A_TEST = "TEST"

        class BConfig(BaseConfig):
            B_TEST = "TEST"

        class CConfig(AConfig, BConfig):
            CONFIGALCHEMY_ENABLE_FUNCTION = True

            def sync_function(self) -> ConfigType:
                return {"A_TEST": "A_TEST", "B_TEST": "B_TEST"}

        self.assertEqual("A_TEST", CConfig().A_TEST)
        self.assertEqual("B_TEST", CConfig().B_TEST)
