import json
from typing import Union, Type, cast, Any


class GenericConfigMixin:
    def __type_check__(self, instance: Any) -> bool:
        return isinstance(instance, self.__class__)

    def __typecast__(self, value: Any) -> Any:
        raise TypeError(f"Object of type {self.__class__.__name__} can not be typecast")


JsonSerializable = Union[int, float, bool, list, dict, str]
JsonSerializableType = Type[JsonSerializable]


class JsonMeta(GenericConfigMixin):
    def __init__(self, origin: JsonSerializableType = dict):
        self.__origin__ = origin

    def __getitem__(self, t: JsonSerializableType) -> JsonSerializable:
        return cast(JsonSerializable, JsonMeta(origin=t))

    def __type_check__(self, instance: Any) -> bool:
        return isinstance(instance, self.__origin__)

    def __typecast__(self, value: Any) -> Any:
        return json.loads(value)


Json = JsonMeta()
