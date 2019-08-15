import json
import unittest
from unittest.mock import Mock

from configalchemy.meta import ConfigMeta, ConfigMetaJSONEncoder


class MetaTestCase(unittest.TestCase):
    def test_usage(self):
        default_value = 0
        int_field = Mock()
        config_meta = ConfigMeta(default_value=default_value, field=int_field)
        self.assertEqual(0, config_meta.value)
        priority = 10
        int_field.validate = Mock(return_value=priority)
        config_meta.set(priority, 0)
        self.assertEqual(priority, config_meta.value)
        priority = 5
        int_field.validate = Mock(return_value=priority)
        config_meta.set(priority, 0)
        self.assertEqual(10, config_meta.value)
        self.assertListEqual(
            [0, 5, 10], [item.value for item in config_meta.value_list]
        )
        self.assertListEqual(
            [0, 5, 10], [item.priority for item in config_meta.value_list]
        )

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
            "[ConfigMetaItem(priority=0, value=0)]", str(config_meta.value_list)
        )


if __name__ == "__main__":
    unittest.main()
