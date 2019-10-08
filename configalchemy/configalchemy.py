"""Main module."""
import asyncio
import errno
import json
import logging
import os
from typing import (
    Any,
    KeysView,
    List,
    Tuple,
    MutableMapping,
    Dict,
    Optional,
    TypeVar,
    Type,
)
from weakref import ref

from configalchemy.field import Field
from configalchemy.meta import ConfigMeta, ConfigMetaJSONEncoder

ConfigType = MutableMapping[str, Any]


class BaseConfig(ConfigType):
    """Initialize the :any:`Config` with the Priority::

        ** config from env > config from local file > config from function > default config **

    Example of class-based configuration::

        class DefaultConfig(BaseConfig):
            TEST = "test"

        config = DefaultConfig()
    """

    # The prefix to construct the full environment variable key to access overrode config.
    CONFIGALCHEMY_ENV_PREFIX = ""
    CONFIGALCHEMY_ENVIRONMENT_VALUE_PRIORITY = 20

    # The the filename of the JSON file. This can either be
    # an absolute filename or a filename relative to the
    # `CONFIGALCHEMY_ROOT_PATH`.
    CONFIGALCHEMY_ROOT_PATH = ""
    CONFIGALCHEMY_CONFIG_FILE = ""
    CONFIGALCHEMY_CONFIG_FILE_VALUE_PRIORITY = 10
    # set to ``True`` if you want silent failure for missing files.
    CONFIGALCHEMY_LOAD_FILE_SILENT = False

    # set to ``True`` if you want to override config from function return value.
    CONFIGALCHEMY_ENABLE_FUNCTION = False
    CONFIGALCHEMY_FUNCTION_VALUE_PRIORITY = 0

    # The priority of config['TEST'] = value,
    # config.TEST = value and
    # config.update(TEST=value)
    CONFIGALCHEMY_SETITEM_PRIORITY = 99

    def __init__(self):
        self.meta: Dict[str, ConfigMeta] = {}

        self._setup()

        #: env
        if self.CONFIGALCHEMY_ENV_PREFIX:
            self._from_env()

        #: config file
        if self.CONFIGALCHEMY_CONFIG_FILE:
            self._from_file()

        #: function
        if self.CONFIGALCHEMY_ENABLE_FUNCTION:
            #: Sync
            self.access_config_from_function(
                priority=self.CONFIGALCHEMY_FUNCTION_VALUE_PRIORITY
            )

            # Async
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                self.access_config_from_coroutine(
                    priority=self.CONFIGALCHEMY_FUNCTION_VALUE_PRIORITY
                )
            )
        global _current_config_ref
        _current_config_ref = ref(self)

    def _setup(self):
        """Setup the default values and field of value from self.
        """
        for key in dir(self):
            if key.isupper():
                self[key] = getattr(self, key)
        return True

    def _from_file(self) -> bool:
        """Updates the values in the config from a JSON file. This function
        behaves as if the JSON object was a dictionary and passed to the
        :meth:`from_mapping` function.
        """
        filename = os.path.join(
            self.CONFIGALCHEMY_ROOT_PATH, self.CONFIGALCHEMY_CONFIG_FILE
        )
        try:
            with open(filename) as f:
                obj = json.load(f)
        except IOError as e:
            if self.CONFIGALCHEMY_LOAD_FILE_SILENT and e.errno in (
                errno.ENOENT,
                errno.EISDIR,
            ):
                return False
            e.strerror = "Unable to load configuration file (%s)" % e.strerror
            raise
        else:
            logging.info(f"Loaded configuration file: {filename}")
            return self.from_mapping(
                obj, priority=self.CONFIGALCHEMY_CONFIG_FILE_VALUE_PRIORITY
            )

    def from_mapping(self, *mappings: ConfigType, priority: int) -> bool:
        """Updates the config like :meth:`update` ignoring items with non-upper
        keys.
        """
        for mapping in mappings:
            for key, value in mapping.items():
                if key.isupper():
                    self._set_value(key, value, priority=priority)
        return True

    def _from_env(self) -> bool:
        """Updates the values in the config from the environment variable.
        """
        for key, value in self.items():
            env_value = os.getenv(f"{self.CONFIGALCHEMY_ENV_PREFIX}{key}")
            if env_value is not None:
                self._set_value(
                    key,
                    env_value,
                    priority=self.CONFIGALCHEMY_ENVIRONMENT_VALUE_PRIORITY,
                )
        return True

    def sync_function(self) -> ConfigType:
        return {}

    async def async_function(self) -> ConfigType:
        return {}

    def access_config_from_function(self, priority: int) -> bool:
        """Updates the values in the config from the sync_access_config_list.
        """
        self.from_mapping(self.sync_function(), priority=priority)
        return True

    async def access_config_from_coroutine(self, priority: int) -> bool:
        """Async updates the values in the config from the async_access_config_list.
        """
        self.from_mapping(await self.async_function(), priority=priority)
        return True

    def _set_value(self, key: str, value: Any, priority: int):
        if key not in self.meta:
            """Setup"""
            self.meta[key] = ConfigMeta(
                default_value=value,
                field=Field(
                    name=key,
                    default_value=value,
                    annotation=getattr(self, "__annotations__", {}).get(key),
                ),
            )
            setattr(self.__class__, key, _ConfigAttribute(key, value))
        else:
            self.meta[key].set(priority=priority, value=value)

    def __getitem__(self, key: str) -> Any:
        """ x.__getitem__(y) <==> x[y] """
        return self.meta[key].value

    def items(self) -> List[Tuple[str, Any]]:  # type: ignore
        return [(key, config_meta.value) for key, config_meta in self.meta.items()]

    def keys(self) -> KeysView[str]:
        return self.meta.keys()

    def __contains__(self, key: object) -> bool:
        return key in self.meta

    def __iter__(self):
        return iter(self.meta)

    def __len__(self) -> int:
        return len(self.meta)

    def __setitem__(self, k, v) -> None:
        self._set_value(k, v, priority=self.CONFIGALCHEMY_SETITEM_PRIORITY)

    def __delitem__(self, key) -> None:
        if len(self.meta[key].items[-1].values) == 1:
            if len(self.meta[key].items) != 1:
                del self.meta[key].items[-1]
        else:
            del self.meta[key].items[-1].values[-1]

    def update(self, __m, **kwargs):
        self.from_mapping(__m, kwargs, priority=self.CONFIGALCHEMY_SETITEM_PRIORITY)

    def get(self, key: str, default=None):
        if key in self.meta:
            return self.meta[key].value
        else:
            return default

    def __bool__(self) -> bool:
        return bool(self.meta)

    def __repr__(self) -> str:
        return repr(self.meta)

    def __str__(self) -> str:
        return repr(self)

    def json(
        self,
        skipkeys: bool = False,
        ensure_ascii: bool = True,
        check_circular: bool = True,
        allow_nan: bool = True,
        sort_keys: bool = False,
        indent: Optional[int] = None,
        separators: Optional[Tuple[str, str]] = None,
        cls: Type[ConfigMetaJSONEncoder] = ConfigMetaJSONEncoder,
    ) -> str:
        return json.dumps(
            self.meta,
            cls=cls,
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            indent=indent,
            separators=separators,
            sort_keys=sort_keys,
        )


class _ConfigAttribute:
    def __init__(self, name: str, default_value: Any):
        self._name = name
        self._default_value = default_value

    def __get__(self, obj: BaseConfig, type=None) -> Any:
        if obj is None:
            return self._default_value
        if self._name not in obj:
            return self._default_value
        else:
            return obj[self._name]

    def __set__(self, instance: BaseConfig, value: Any) -> None:
        instance[self._name] = value


_current_config_ref = ref(object)
_CurrentConfigType = TypeVar("_CurrentConfigType", bound=BaseConfig)


def get_current_config(config_type: Type[_CurrentConfigType]) -> _CurrentConfigType:
    # """This API can and should only be used in lazy loading current config instance in the runtime"""
    current_config = _current_config_ref()
    if not isinstance(current_config, config_type):
        raise RuntimeError(f"There is no instance of type {config_type}")
    return current_config
