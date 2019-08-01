"""Main module."""
import asyncio
import errno
import json
import logging
import os
from collections import defaultdict
from threading import Lock
from typing import (
    Any,
    Callable,
    Coroutine,
    DefaultDict,
    KeysView,
    List,
    Tuple,
    MutableMapping,
)


_miss = lambda _: _

ConfigType = MutableMapping[str, Any]


class _ConfigMeta:
    def __init__(self, default=None):
        self.value_type: Callable[[Any], Any] = _miss
        self.default_value = default
        self.function_value = None
        self.config_file_value = None
        self.env_value = None

    def get_config(self) -> Any:
        if self.env_value is not None:
            return self.env_value
        elif self.config_file_value is not None:
            return self.config_file_value
        elif self.function_value is not None:
            return self.function_value
        else:
            return self.default_value

    def get(self) -> Any:
        return self.get_config()

    def set(self, priority: int, value: Any) -> bool:
        value = self.value_type(value)
        if priority == 0:
            self.default_value = value
        elif priority == 1:
            self.function_value = value
        elif priority == 2:
            self.config_file_value = value
        else:
            self.env_value = value
        return True


class BaseConfig(ConfigType):
    """Initialize the :any:`Config` with the Priority::

        ** config from env > config from local file > config from function > default config **

    Example of module-based configuration::

        pass
    """

    ENV_PREFIX = ""
    CONFIG_FILE = ""
    ENABLE_FUNCTION = False

    def __init__(
        self,
        function_list: List[Callable[[Any], ConfigType]] = None,
        coroutine_function_list: List[
            Callable[[Any], Coroutine[Any, Any, ConfigType]]
        ] = None,
        root_path: str = "",
    ):
        self.lock = Lock()
        self.config_meta: DefaultDict[str, _ConfigMeta] = defaultdict(_ConfigMeta)
        self.root_path = root_path
        self.function_list = function_list or []
        self.coroutine_function_list = coroutine_function_list or []

        self._setup()

        #: env
        env_prefix = self.get("ENV_PREFIX", "")
        if env_prefix:
            self.from_env(prefix=env_prefix)

        #: local config file
        config_file = self.get("CONFIG_FILE", "")
        if config_file:
            self.from_file(config_file)

        #: function
        if self.get("ENABLE_FUNCTION", False):
            #: Sync
            if self.function_list:
                self.access_config_from_function_list()

            # Async
            loop = asyncio.get_event_loop()
            if self.coroutine_function_list:
                loop.run_until_complete(
                    self.access_config_from_coroutine_function_list()
                )

    def _setup(self):
        """Setup the default values and type of value from self.
        """
        for key in dir(self):
            if key.isupper():
                default_value = getattr(self, key)
                self._set_value(key, default_value, priority=0)
                self.config_meta[key].value_type = type(default_value)
                setattr(self.__class__, key, _ConfigAttribute(key))
        return True

    def from_file(self, filename: str, silent: bool = False, priority: int = 2) -> bool:
        """Updates the values in the config from a JSON file. This function
        behaves as if the JSON object was a dictionary and passed to the
        :meth:`from_mapping` function.

        :param str filename: the filename of the JSON file. This can either be
                            an absolute filename or a filename relative to the
                            root path.
        :param bool silent: set to ``True`` if you want silent failure for missing
                       files.

        """
        filename = os.path.join(self.root_path, filename)
        try:
            with open(filename) as f:
                obj = json.load(f)
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = "Unable to load configuration file (%s)" % e.strerror
            raise
        else:
            logging.info(f"Loaded configuration file: {filename}")
            return self.from_mapping(obj, priority=priority)

    def from_mapping(self, *mappings: ConfigType, priority: int) -> bool:
        """Updates the config like :meth:`update` ignoring items with non-upper
        keys.
        """
        for mapping in mappings:
            for key, value in mapping.items():
                if key.isupper():
                    self._set_value(key, value, priority=priority)
        return True

    def from_env(self, prefix: str, priority: int = 3) -> bool:
        """Updates the values in the config from the environment variable.

        :param str prefix: The prefix to construct the full environment variable
                        with the key.

        """
        for key, value in self.items():
            env_value = os.getenv(f"{prefix}{key}")
            if env_value is not None:
                self._set_value(key, env_value, priority=priority)
        return True

    def access_config_from_function_list(self, priority: int = 1) -> bool:
        """Updates the values in the config from the sync_access_config_list.


        """
        for function in self.function_list:
            self.from_mapping(function(self), priority=priority)
        return True

    async def access_config_from_coroutine_function_list(
        self, priority: int = 1
    ) -> bool:
        """Async updates the values in the config from the async_access_config_list.

        """
        for coroutine_function in self.coroutine_function_list:
            self.from_mapping(await coroutine_function(self), priority=priority)
        return True

    def _set_value(self, key: str, value: Any, priority: int):
        with self.lock:
            self.config_meta[key].set(priority=priority, value=value)

    def __getitem__(self, key: str) -> Any:
        """ x.__getitem__(y) <==> x[y] """
        with self.lock:
            if key not in self.config_meta:
                raise KeyError(key)
            return self.config_meta[key].get()

    def items(self) -> List[Tuple[str, Any]]:  # type: ignore
        return [
            (key, config_meta.get()) for key, config_meta in self.config_meta.items()
        ]

    def keys(self) -> KeysView[str]:
        return self.config_meta.keys()

    def __contains__(self, key: object) -> bool:
        return key in self.config_meta

    def __iter__(self):
        return iter(self.config_meta)

    def __len__(self) -> int:
        return len(self.config_meta)

    def __setitem__(self, k, v) -> None:
        self._set_value(k, v, priority=3)

    def __delitem__(self, key) -> None:
        del self.config_meta[key]

    def update(self, __m, **kwargs):
        self.from_mapping(__m, kwargs, priority=3)

    def get(self, key: str, default=None):
        with self.lock:
            return self.config_meta.get(key, _ConfigMeta(default=default)).get()

    def __bool__(self) -> bool:
        return bool(self.config_meta)


class _ConfigAttribute:
    def __init__(self, name: str):
        self._name = name

    def __get__(self, obj: BaseConfig, type=None) -> Any:
        if obj is None:
            return self
        return obj[self._name]

    def __set__(self, instance: BaseConfig, value: Any) -> None:
        instance[self._name] = value
