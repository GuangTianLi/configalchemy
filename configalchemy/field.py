from typing import Any, Union, Callable

from configalchemy.types import DEFAULT_TYPE_CAST


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
    __slots__ = (
        "name",
        "annotation",
        "value_type",
        "default_value",
        "type_check",
        "typecast",
    )

    def __init__(self, *, name: str, annotation: Any, default_value: Any):
        self.name = name
        self.annotation = annotation
        self.default_value = default_value
        self.value_type = type(default_value)
        self.type_check: Callable[[Any], bool] = self._type_check
        self.typecast: Callable[[Any, int], Any] = self._typecast

        self.prepare()

        if self.value_type in DEFAULT_TYPE_CAST:
            self.type_check = DEFAULT_TYPE_CAST[self.value_type].__type_check__
            self.typecast = DEFAULT_TYPE_CAST[self.value_type].__typecast__

        if getattr(self.default_value, "__type_check__", None):
            self.type_check = self.default_value.__type_check__
        if getattr(self.default_value, "__typecast__", None):
            self.typecast = self.default_value.__typecast__

        if getattr(self.annotation, "__type_check__", None):
            self.type_check = self.annotation.__type_check__
        if getattr(self.annotation, "__typecast__", None):
            self.typecast = self.annotation.__typecast__

    def prepare(self) -> None:
        origin = getattr(self.annotation, "__origin__", None)
        if origin is None:
            # field is not "typing" object eg. Union etc.
            return
        if origin is Union:
            self.value_type = self.annotation.__args__
            self.typecast = lambda x, p: self.value_type[0](x)
            return

    def validate(self, value: Any, priority: int = 0) -> Any:
        if self.type_check(value):
            return value
        else:
            try:
                return self.typecast(value, priority)
            except Exception as e:
                raise ValidateException(self.name, value) from e

    def _type_check(self, value: Any) -> bool:
        return isinstance(value, self.value_type)

    def _typecast(self, value: Any, priority: int) -> Any:
        return self.value_type(value)
