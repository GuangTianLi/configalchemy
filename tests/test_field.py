import json
import unittest
from typing import Optional, List, Any
from unittest.mock import Mock

from configalchemy.field import Field, ValidateException
from configalchemy.types import Json


class FieldTestCase(unittest.TestCase):
    def test_validate(self):
        int_field = Field(name="TEST", default_value=0, annotation=None)
        for value in [b"0", "0"]:
            self.assertEqual(0, int_field.validate(value))
        with self.assertRaises(ValidateException) as e:
            int_field.validate(".0")
        self.assertIn(".0", str(e.exception))
        self.assertIn(str(type(".0")), str(e.exception))
        self.assertEqual("TEST", e.exception.name)
        self.assertEqual(".0", e.exception.value)

    def test_bool_validate(self):
        bool_field = Field(name="TEST", default_value=False, annotation=None)
        for value in ["true", "1", "yes", "y", 1]:
            self.assertTrue(bool_field.validate(value))
        for value in ["0", "false", "False", "No", 0]:
            self.assertFalse(bool_field.validate(value))
        self.assertTrue(bool_field.validate(True))
        self.assertFalse(bool_field.validate(False))

    def test_union_type(self):
        optional_field = Field(
            name="TEST", default_value=None, annotation=Optional[int]
        )
        self.assertEqual(1, optional_field.validate(1))
        self.assertEqual(1, optional_field.validate("1"))

    def test_json_type(self):
        value_type = Json[list]
        self.assertIs(value_type, Json[list])
        default_value: value_type = []
        json_field = Field(
            name="TEST", default_value=default_value, annotation=value_type
        )
        self.assertEqual([1], json_field.validate([1]))
        self.assertEqual([1], json_field.validate(json.dumps([1])))

        default_value: Json[List[int]] = [1, 2]
        json_field = Field(
            name="TEST", default_value=default_value, annotation=Json[List[int]]
        )
        self.assertEqual([1], json_field.validate(json.dumps([1])))

    def test_generic_field(unittest_self):
        class MyType:
            ...

        my_type = MyType()
        generic_field = Field(name="TEST", default_value=my_type, annotation=None)
        unittest_self.assertEqual(my_type, generic_field.validate(my_type))
        with unittest_self.assertRaises(ValidateException):
            generic_field.validate("typecast")

        value = ["1", "2"]
        typecast = Mock(return_value=value)

        class TestGenericConfigMixin:
            @classmethod
            def __type_check__(cls, instance) -> bool:
                return isinstance(instance, list)

            @classmethod
            def __typecast__(cls, value: Any) -> list:
                return typecast(value)

        generic_config = TestGenericConfigMixin()
        generic_field = Field(
            name="TEST", default_value=generic_config, annotation=None
        )
        unittest_self.assertEqual(value, generic_field.validate(value))
        unittest_self.assertFalse(typecast.called)
        unittest_self.assertEqual(value, generic_field.validate("typecast"))
        typecast.assert_called_with("typecast")


if __name__ == "__main__":
    unittest.main()
