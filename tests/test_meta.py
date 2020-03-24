import json
import unittest
from unittest.mock import Mock

from configalchemy.meta import ConfigMeta, ConfigMetaJSONEncoder


class MetaTestCase(unittest.TestCase):
    def test_usage(self):
        default_value = 0
        int_field = Mock()
        config_meta = ConfigMeta(default_value=default_value, field=int_field)
        with config_meta:
            priority = 0
            int_field.validate = Mock(return_value=priority)
            config_meta.set(priority, 0)
            self.assertEqual(0, config_meta.value)
            priority = 10
            int_field.validate = Mock(return_value=priority)
            config_meta.set(priority, 0)
            self.assertEqual(priority, config_meta.value)
            priority = 5
            int_field.validate = Mock(return_value=priority)
            config_meta.set(priority, 0)
            self.assertEqual(10, config_meta.value)

            self.assertEqual(0, config_meta.items[0].priority)
            self.assertEqual(0, config_meta.items[0].value)
            self.assertEqual(0, config_meta.items[1].priority)
            self.assertEqual(0, config_meta.items[1].value)
            self.assertEqual(5, config_meta.items[2].priority)
            self.assertEqual(5, config_meta.items[2].value)
            self.assertEqual(10, config_meta.items[3].priority)
            self.assertEqual(10, config_meta.items[3].value)

    def test_json_encode(self):
        default_value = 0
        int_field = Mock()
        config_meta = ConfigMeta(default_value=default_value, field=int_field)
        self.assertEqual(
            json.dumps({"TEST": default_value}),
            json.dumps({"TEST": config_meta}, cls=ConfigMetaJSONEncoder),
        )
        self.assertEqual("0", str(config_meta))
        self.assertEqual("0", repr(config_meta))
        self.assertEqual(
            "[ConfigMetaItem(priority=0, value=0)]", str(config_meta.items)
        )


if __name__ == "__main__":
    unittest.main()
