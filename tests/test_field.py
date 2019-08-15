import unittest
from typing import Optional
from unittest.mock import patch, Mock

from configalchemy.ext.generic_config import ListConfig, DictConfig
from configalchemy.field import Field, ValidateException


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
        with patch.object(Field, "_typecast") as typecast:
            self.assertEqual(1, optional_field.validate(1))
            self.assertFalse(typecast.called)
        self.assertEqual(1, optional_field.validate("1"))

    def test_generic_field(self):
        value = ["1", "2"]
        typecast = Mock(return_value=value)
        list_config = ListConfig(value, typecast=typecast)
        generic_field = Field(name="TEST", default_value=list_config, value_type=None)
        with patch.object(Field, "_typecast") as _typecast:
            self.assertEqual(value, generic_field.validate(value))
            self.assertFalse(_typecast.called)
        self.assertEqual(value, generic_field.validate("typecast"))
        typecast.assert_called_with("typecast")

        value = {"1": 1}
        typecast = Mock(return_value=value)
        dict_config = DictConfig(value, typecast=typecast)
        generic_field = Field(name="TEST", default_value=dict_config, value_type=None)
        with patch.object(Field, "_typecast") as _typecast:
            self.assertEqual(value, generic_field.validate(value))
            self.assertFalse(_typecast.called)
        self.assertEqual(value, generic_field.validate("typecast"))
        typecast.assert_called_with("typecast")


if __name__ == "__main__":
    unittest.main()
