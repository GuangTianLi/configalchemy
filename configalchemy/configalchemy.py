"""Main module."""
import asyncio
import errno
import json
import logging
import os
from threading import Lock
from typing import Any, Callable, Coroutine, KeysView, List, Tuple, MutableMapping, Dict

_miss = lambda _: _

ConfigType = MutableMapping[str, Any]


class ConfigItem:
    def __init__(self, priority: int, value: Any):
        self.priority = priority
        self.value = value

    def __repr__(self) -> str:
        return f"'priority : {self.priority}, value : {self.value}'"

    def __str__(self) -> str:
        return repr(self)


class _ConfigMeta:
    def __init__(self, default_value: Any):
        self.typecast: Callable[[Any], Any] = getattr(
            default_value, "__typecast__", type(default_value)
        )
        self.instance_check: Callable[[Any], bool] = getattr(
            default_value,
            "__isinstance__",
            lambda x: isinstance(x, type(default_value)),
        )
        self.value_list: List[ConfigItem] = [ConfigItem(0, default_value)]

    @property
    def value(self) -> Any:
        return self.value_list[-1].value

    def set(self, priority: int, value: Any) -> None:
        if not self.instance_check(value):
            value = self.typecast(value)
        item = ConfigItem(priority, value)
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


class BaseConfig(ConfigType):
    """Initialize the :any:`Config` with the Priority::

        ** config from env > config from local file > config from function > default config **

    Example of module-based configuration::

        class DefaultObject(BaseConfig):
            TEST = "test"

        config = DefaultObject()
    """

    # The prefix to construct the full environment variable key to access overrode config.
    CONFIGALCHEMY_ENV_PREFIX = ""
    CONFIGALCHEMY_ENVIRONMENT_VALUE_PRIORITY = 3

    # The the filename of the JSON file. This can either be
    # an absolute filename or a filename relative to the
    # `CONFIGALCHEMY_ROOT_PATH`.
    CONFIGALCHEMY_ROOT_PATH = ""
    CONFIGALCHEMY_CONFIG_FILE = ""
    CONFIGALCHEMY_CONFIG_FILE_VALUE_PRIORITY = 2
    # set to ``True`` if you want silent failure for missing files.
    CONFIGALCHEMY_LOAD_FILE_SILENT = False

    # set to ``True`` if you want to override config from function return value.
    CONFIGALCHEMY_ENABLE_FUNCTION = False
    CONFIGALCHEMY_FUNCTION_VALUE_PRIORITY = 1

    # The priority of config['TEST'] = value,
    # config.TEST = value and
    # config.update(TEST=value)
    CONFIGALCHEMY_SETITEM_PRIORITY = 99

    def __init__(
        self,
        function_list: List[Callable[[Any], ConfigType]] = None,
        coroutine_function_list: List[
            Callable[[Any], Coroutine[Any, Any, ConfigType]]
        ] = None,
    ):
        self.lock = Lock()
        self.meta: Dict[str, _ConfigMeta] = {}
        self.function_list = function_list or []
        self.coroutine_function_list = coroutine_function_list or []

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
            if self.function_list:
                self.access_config_from_function_list(
                    priority=self.CONFIGALCHEMY_FUNCTION_VALUE_PRIORITY
                )

            # Async
            loop = asyncio.get_event_loop()
            if self.coroutine_function_list:
                loop.run_until_complete(
                    self.access_config_from_coroutine_function_list(
                        priority=self.CONFIGALCHEMY_FUNCTION_VALUE_PRIORITY
                    )
                )
        super().__init__()

    def _setup(self):
        """Setup the default values and type of value from self.
        """
        for key in dir(self):
            if key.isupper():
                default_value = getattr(self, key)
                self.meta[key] = _ConfigMeta(default_value=default_value)
                setattr(self.__class__, key, _ConfigAttribute(key, default_value))
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

    def access_config_from_function_list(self, priority: int) -> bool:
        """Updates the values in the config from the sync_access_config_list.
        """
        for function in self.function_list:
            self.from_mapping(function(self), priority=priority)
        return True

    async def access_config_from_coroutine_function_list(self, priority: int) -> bool:
        """Async updates the values in the config from the async_access_config_list.
        """
        for coroutine_function in self.coroutine_function_list:
            self.from_mapping(await coroutine_function(self), priority=priority)
        return True

    def _set_value(self, key: str, value: Any, priority: int):
        with self.lock:
            self.meta[key].set(priority=priority, value=value)

    def __getitem__(self, key: str) -> Any:
        """ x.__getitem__(y) <==> x[y] """
        with self.lock:
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
        del self.meta[key]

    def update(self, __m, **kwargs):
        self.from_mapping(__m, kwargs, priority=self.CONFIGALCHEMY_SETITEM_PRIORITY)

    def get(self, key: str, default=None):
        with self.lock:
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


class _ConfigAttribute:
    def __init__(self, name: str, default_value: Any):
        self._name = name
        self._default_value = default_value

    def __get__(self, obj: BaseConfig, type=None) -> Any:
        if obj is None:
            return self
        if self._name not in obj:
            return self._default_value
        else:
            return obj[self._name]

    def __set__(self, instance: BaseConfig, value: Any) -> None:
        instance[self._name] = value
