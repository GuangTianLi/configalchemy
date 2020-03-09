from json import JSONEncoder
from typing import Any, List, MutableMapping

from configalchemy.field import Field

ConfigType = MutableMapping[str, Any]


class ConfigMetaItem:
    __slots__ = ("priority", "values")

    def __init__(self, priority: int, value: Any):
        self.priority = priority
        self.values = [value]

    def __repr__(self) -> str:
        return f"ConfigMetaItem(priority={self.priority}, value={self.values})"

    def __str__(self) -> str:
        return repr(self)


class ConfigMeta:
    __slots__ = ("field", "items")

    def __init__(self, default_value: Any, field: Field, priority: int = 0):
        self.field = field
        self.items: List[ConfigMetaItem] = [ConfigMetaItem(priority, default_value)]

    @property
    def value(self) -> Any:
        return self.items[-1].values[-1]

    def set(self, priority: int, value: Any) -> None:
        value = self.field.validate(value)
        length = len(self.items)
        for index in range(length, 0, -1):
            if self.items[index - 1].priority < priority:
                item = ConfigMetaItem(priority, value)
                self.items.insert(index, item)
                break
            elif self.items[index - 1].priority == priority:
                self.items[index - 1].values.append(value)
                break

    def __repr__(self) -> str:
        return repr(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __enter__(self):
        """Prepare to implement optimistic raw lock if necessary"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class ConfigMetaJSONEncoder(JSONEncoder):
    def default(self, o) -> Any:
        if isinstance(o, ConfigMeta):
            return o.value
        super().default(o)
