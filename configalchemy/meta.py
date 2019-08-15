from json import JSONEncoder
from typing import Any, List, MutableMapping

from configalchemy.field import Field

ConfigType = MutableMapping[str, Any]


class ConfigMetaItem:
    def __init__(self, priority: int, value: Any):
        self.priority = priority
        self.value = value

    def __repr__(self) -> str:
        return f"ConfigMetaItem(priority={self.priority}, value={self.value})"

    def __str__(self) -> str:
        return repr(self)


class ConfigMeta:
    def __init__(self, default_value: Any, field: Field):
        self.field = field
        self.value_list: List[ConfigMetaItem] = [ConfigMetaItem(0, default_value)]

    @property
    def value(self) -> Any:
        return self.value_list[-1].value

    def set(self, priority: int, value: Any) -> None:
        value = self.field.validate(value)
        item = ConfigMetaItem(priority, value)
        length = len(self.value_list)
        for index in range(length - 1, 0, -1):
            if self.value_list[index - 1].priority <= priority:
                self.value_list.insert(index, item)
                break
        else:
            self.value_list.insert(1, item)

    def __repr__(self) -> str:
        return repr(self.value)

    def __str__(self) -> str:
        return str(self.value)


class ConfigMetaJSONEncoder(JSONEncoder):
    def default(self, o: ConfigMeta) -> Any:
        if isinstance(o, ConfigMeta):
            return o.value
        super().default(o)
