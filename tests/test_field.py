import json
import unittest
from typing import Optional, Any, List
from unittest.mock import patch, Mock

from configalchemy.field import Field, ValidateException
from configalchemy.types import Json, GenericConfigMixin


class FieldTestCase(unittest.TestCase):
    def test_validate(self):
        int_field = Field(name="TEST", default_value=0, value_type=int)
        for value in [b"0", "0"]:
            self.assertEqual(0, int_field.validate(value))
        with self.assertRaises(ValidateException) as e:
            int_field.validate(".0")
        self.assertIn(".0", str(e.exception))
        self.assertIn(str(type(".0")), str(e.exception))
        self.assertEqual("TEST", e.exception.name)
        self.assertEqual(".0", e.exception.value)

    def test_union_type(self):
        optional_field = Field(
            name="TEST", default_value=None, value_type=Optional[int]
        )
        self.assertEqual(1, optional_field.validate(1))
        self.assertEqual(1, optional_field.validate("1"))

    def test_json_type(self):
        value_type = Json[list]
        default_value: value_type = []
        json_field = Field(
            name="TEST", default_value=default_value, value_type=value_type
        )
        with patch.object(value_type, "__typecast__") as mock:
            self.assertEqual([1], json_field.validate([1]))
            self.assertFalse(mock.called)
        self.assertEqual([1], json_field.validate(json.dumps([1])))

        default_value: Json[List[int]] = [1, 2]
        json_field = Field(
            name="TEST", default_value=default_value, value_type=Json[List[int]]
        )
        self.assertEqual([1], json_field.validate(json.dumps([1])))

    def test_generic_field(unittest_self):
        value = ["1", "2"]
        typecast = Mock(return_value=value)

        class TestGenericConfigMixin(GenericConfigMixin):
            def __type_check__(self, instance) -> bool:
                return isinstance(instance, list)

            def __typecast__(self, value: Any) -> Any:
                return typecast(value)

        generic_config = TestGenericConfigMixin()
        generic_field = Field(
            name="TEST", default_value=generic_config, value_type=None
        )
        unittest_self.assertEqual(value, generic_field.validate(value))
        unittest_self.assertFalse(typecast.called)
        unittest_self.assertEqual(value, generic_field.validate("typecast"))
        typecast.assert_called_with("typecast")


if __name__ == "__main__":
    unittest.main()
