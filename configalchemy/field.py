from typing import Type, Any, Union, Optional, Callable

from configalchemy.types import JsonMeta

AnyType = Optional[Type[Any]]


class ValidateException(Exception):
    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return f"""{self.name}'s value is invalid:

value: {self.value} 
type {type(self.value)}
"""

    def __str__(self) -> str:
        return repr(self)


class Field:
    __slots__ = ("name", "value_type", "default_value", "type_check", "typecast")

    def __init__(self, *, name: str, value_type: AnyType, default_value: Any):
        self.name = name
        self.value_type = value_type or type(default_value)
        self.default_value = default_value
        self.type_check: Callable[[Any], bool] = self._type_check
        self.typecast: Callable[[Any], Any] = self._typecast

        self.prepare()

        if getattr(self.default_value, "__type_check__", None):
            self.type_check = self.default_value.__type_check__
        if getattr(self.default_value, "__typecast__", None):
            self.typecast = self.default_value.__typecast__

    def prepare(self) -> None:
        if isinstance(self.value_type, JsonMeta):
            self.typecast = self.value_type.__typecast__
            self.type_check = self.value_type.__type_check__
            return

        origin = getattr(self.value_type, "__origin__", None)
        if origin is None:
            # field is not "typing" object eg. Union etc.
            return
        if origin is Union:
            self.value_type = self.value_type.__args__
            self.typecast = lambda x: self.value_type[0](x)
            return

    def validate(self, value: Any) -> Any:
        if self.type_check(value):
            return value
        else:
            try:
                return self.typecast(value)
            except Exception as e:
                raise ValidateException(self.name, value) from e

    def _type_check(self, value: Any) -> bool:
        return isinstance(value, self.value_type)

    def _typecast(self, value: Any) -> Any:
        return self.value_type(value)
