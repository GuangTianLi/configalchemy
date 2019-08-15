from typing import Type, Any, Union, Optional

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
    __slots__ = ("name", "value_type", "default_value")

    def __init__(self, *, name: str, value_type: AnyType, default_value: Any):
        self.name = name
        self.value_type = value_type or type(default_value)
        self.default_value = default_value
        self.prepare()

    def prepare(self) -> None:
        origin = getattr(self.value_type, "__origin__", None)
        if origin is None:
            # field is not "typing" object eg. Union etc.
            return
        if origin is Union:
            self.value_type = self.value_type.__args__
            return

    def validate(self, value: Any) -> Any:
        if self._instance_check(value):
            return value
        else:
            try:
                return self._typecast(value)
            except Exception as e:
                raise ValidateException(self.name, value) from e

    def _instance_check(self, value: Any) -> bool:
        if getattr(self.default_value, "__instancecheck__", None):
            return self.default_value.__instancecheck__(value)
        return isinstance(value, self.value_type)

    def _typecast(self, value: Any) -> Any:
        if getattr(self.default_value, "__typecast__", None):
            return self.default_value.__typecast__(value)
        if isinstance(self.value_type, tuple):
            return self.value_type[0](value)
        else:
            return self.value_type(value)
