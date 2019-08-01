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
        class DefaultObject(BaseConfig):
            TEST = "test"

        config = DefaultObject()

        self.assertEqual("test", config["TEST"])
        self.assertEqual("test", config.TEST)
        with self.assertRaises(KeyError):
            _ = config["NOT_EXIST"]

        def test_double_star(**kw):
            self.assertEqual(config, kw)

        test_double_star(**config)
        self.assertEqual("NOT_EXIST", config.get("NOT_EXIST", "NOT_EXIST"))

        self.assertTrue(config)
        self.assertTrue("TEST" in config)
        self.assertEqual(len(config), len(list(iter(config))))

        config.update(dict(TEST="update"))
        self.assertEqual("update", config["TEST"])
        self.assertEqual("update", config.TEST)
        del config["TEST"]
        with self.assertRaises(KeyError):
            tmp = config.TEST
        with self.assertRaises(KeyError):
            tmp = config["TEST"]

    def test_default_config_update_from_json(self):
        class DefaultObject(BaseConfig):
            CONFIG_FILE = self.json_file

            JSON_TEST = "default"

        config = DefaultObject()

        self.assertEqual("JSON_TEST", config["JSON_TEST"])
        self.assertEqual("JSON_TEST", config.JSON_TEST)

    def test_config_file_not_exist(self):
        class DefaultObject(BaseConfig):
            CONFIG_FILE = "not.exist"

        with self.assertRaises(IOError):
            DefaultObject()

    def test_config_with_env(self):
        os.environ["test_TEST"] = "changed"

        class DefaultObject(BaseConfig):
            ENV_PREFIX = "test_"
            TEST = "default"

        config = DefaultObject()
        self.assertEqual("changed", config["TEST"])
        self.assertEqual("changed", config.TEST)

    def test_update_config_from_function(self):
        class DefaultObject(BaseConfig):
            ENABLE_FUNCTION = True
            TEST = "default"

        def get_config(current_config: DefaultObject) -> ConfigType:
            self.assertTrue(current_config["ENABLE_FUNCTION"])
            return {"TEST": "changed"}

        config = DefaultObject(function_list=[get_config])
        self.assertEqual("changed", config["TEST"])
        self.assertEqual("changed", config.TEST)

    def test_async_update_config_from_function(self):
        class DefaultObject(BaseConfig):
            ENABLE_FUNCTION = True
            TEST = "default"

        async def get_config_async(current_config: DefaultObject) -> ConfigType:
            self.assertTrue(current_config["ENABLE_FUNCTION"])
            return {"TEST": "changed"}

        config = DefaultObject(coroutine_function_list=[get_config_async])
        self.assertEqual("changed", config["TEST"])
        self.assertEqual("changed", config.TEST)

    def test_config_priority(self):
        os.environ["test_FOURTH"] = "3"
        current_json_file = "test_priority.json"

        with open(current_json_file, "w") as fp:
            json.dump({"THIRD": "2", "FOURTH": "2"}, fp)

        class DefaultObject(BaseConfig):
            # env
            ENV_PREFIX = "test_"
            # file
            CONFIG_FILE = current_json_file
            ENABLE_FUNCTION = True

            FIRST = 0
            SECOND = "0"
            THIRD = "0"
            FOURTH = 0

        def get_config(current_config: DefaultObject) -> dict:
            return {"SECOND": "1", "FOURTH": "1"}

        async def get_config_async(current_config: DefaultObject) -> dict:
            return {"THIRD": 1, "FOURTH": 1}

        config = DefaultObject(
            function_list=[get_config], coroutine_function_list=[get_config_async]
        )
        self.assertEqual(0, config["FIRST"])
        self.assertEqual("1", config["SECOND"])
        self.assertEqual("2", config["THIRD"])
        self.assertEqual(3, config["FOURTH"])
        config.access_config_from_function_list()
        self.assertEqual(3, config["FOURTH"])
        os.remove(current_json_file)
