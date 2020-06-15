import os
from json import JSONEncoder
from typing import Any, List, MutableMapping

from configalchemy.field import Field
from configalchemy.utils import find_caller

ConfigType = MutableMapping[str, Any]

CONFIG_ALCHEMY_VERBOSITY = os.getenv("CONFIG_ALCHEMY_VERBOSITY", "")


class ConfigMetaItem:
    __slots__ = ("priority", "value", "setter")

    if CONFIG_ALCHEMY_VERBOSITY:

        def __init__(self, priority: int, value: Any):
            self.priority = priority
            self.value = value
            try:
                self.setter = find_caller()
            except ValueError:
                self.setter = None

    else:

        def __init__(self, priority: int, value: Any):
            self.priority = priority
            self.value = value
            self.setter = None

    def __repr__(self) -> str:
        return f"ConfigMetaItem(priority={self.priority}, value={self.value})"

    __str__ = __repr__


class ConfigMeta:
    __slots__ = ("field", "items")

    def __init__(self, default_value: Any, field: Field, priority: int = 0):
        self.field = field
        self.items: List[ConfigMetaItem] = [ConfigMetaItem(priority, default_value)]

    @property
    def value(self) -> Any:
        return self.items[-1].value

    def set(self, priority: int, value: Any) -> None:
        value = self.field.validate(value)
        length = len(self.items)
        item = ConfigMetaItem(priority, value)
        for index in range(length, 0, -1):
            if self.items[index - 1].priority <= priority:
                self.items.insert(index, item)
                break
        else:
            self.items.insert(0, ConfigMetaItem(priority, value))

    def __repr__(self) -> str:
        return repr(self.value)

    __str__ = __repr__

    def __enter__(self):
        """Prepare to implement optimistic raw lock if necessary"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class ConfigMetaJSONEncoder(JSONEncoder):
    def default(self, o) -> Any:
        if isinstance(o, ConfigMeta):
            return o.value
        return super().default(o)
