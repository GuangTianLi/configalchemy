=====
Usage
=====

To use ConfigAlchemy in a project.

.. note:: the configuration key should be **uppercase**.

.. code-block:: python

    from configalchemy import BaseConfig

    class DefaultConfig(BaseConfig):
        TEST = "test"

    config = DefaultConfig()

How to Use the Config
==============================================

Inherit from :any:`BaseConfig` to dynamic configure your configuration.

.. note:: Default Priority
    Environment Variables > File > Function Return Value > Default Value

Define the Default Config Class
-----------------------------------------

Inherit from :any:`BaseConfig` to define your config value explicitly:

.. note:: the config key should be **uppercase**.

.. code-block:: python

    from configalchemy import BaseConfig

    class DefaultConfig(BaseConfig):
        DEBUG = False
        TESTING = False
        DATABASE_URI = 'sqlite:///:memory:'

    class ProductionConfig(DefaultConfig):
        DATABASE_URI = 'mysql://user@localhost/foo'

    class DevelopmentConfig(DefaultConfig):
        DEBUG = True

    class TestingConfig(DefaultConfig):
        TESTING = True

    config = DevelopmentConfig()
    >>> config.DEBUG
    True

Enable Environment Variables
----------------------------------------

Define the **CONFIGALCHEMY_ENV_PREFIX** to enable access config from environment variables:

.. note:: The :any:`BaseConfig` will try to load config value with f'{CONFIGALCHEMY_ENV_PREFIX}{key}'.

.. code-block:: python

    from configalchemy import BaseConfig
    import os

    os.environ['TEST_NAME'] = 'env'

    class DefaultConfig(BaseConfig):
        CONFIGALCHEMY_ENV_PREFIX = 'TEST_'
        NAME = 'base'

    config = DefaultConfig()

    >>> config['NAME']
    env

Enable Configure from File
---------------------------------

Define **CONFIGALCHEMY_CONFIG_FILE** to enable access config from config file:

.. note:: Support JSON file

.. code-block:: python

    from configalchemy import BaseConfig

    class DefaultConfig(BaseConfig):
        CONFIGALCHEMY_CONFIG_FILE = 'test.json' #: etc: {'NAME': 'json'}
        NAME = 'base'

    config = DefaultConfig()

    >>> config['NAME']
    json

Enable Configure with function return value
----------------------------------------------------
Define **CONFIGALCHEMY_ENABLE_FUNCTION** to configure from function return value (support coroutine):

.. code-block:: python

    from configalchemy import BaseConfig, ConfigType


    class SyncDefaultConfig(BaseConfig):
        CONFIGALCHEMY_ENABLE_FUNCTION = True
        TYPE = "base"

        def configuration_function(self) -> ConfigType:
            return {"TYPE": "sync"}


    class AsyncDefaultConfig(BaseConfig):
        CONFIGALCHEMY_ENABLE_FUNCTION = True
        TYPE = "base"

        async def async_function(self) -> ConfigType:
            return {"TYPE": "async"}


    sync_config = SyncDefaultConfig()
    async_config = AsyncDefaultConfig()

    >>> sync_config['TYPE']
    sync
    >>> async_config['NAME']
    async


Auto Validation and Dynamic typecast
==============================================

When new value is assigned to config, the value will be validated and typecast if possible and the process bases on
`default value` or `type annotations`.

.. code-block:: python

    from typing import Optional
    from configalchemy import BaseConfig

    class DefaultConfig(BaseConfig):
        id = 1
        name = "Tony"
        limit: Optional[int] = None

    config = DefaultConfig()
    config.id = '10'
    print(config.id) # 10
    config.limit = 10
    print(config.limit) # 10

Json Type
----------------------------------------------------

You can use Json data type - `configalchemy` will use json.loads to typecast.

.. code-block:: python

    import json

    from configalchemy import BaseConfig
    from configalchemy.types import Json

    class DefaultConfig(BaseConfig):
        TEST_LIST: Json[list] = ["str"]
        TEST_DICT: Json[dict] = {"name": "default"}

    config = DefaultConfig()
    config.TEST_LIST = json.dumps(["test"])
    config.TEST_LIST
    >>> ["test"]
    config.TEST_DICT = json.dumps({"name": "test"})
    config.TEST_DICT
    >>> {"name": "test"}


Advanced Usage
=====================================

Singleton
------------------------------------------

.. code-block:: python
    from configalchemy import SingletonMetaClass
    class FrameworkConfig(BaseConfig, metaclass=SingletonMetaClass):
        NAME = "nested"

    # your framework code
    current_config = FrameworkConfig.instance()

Nested Config for Modular Purpose
------------------------------------------

.. code-block:: python

    class NestedConfig(BaseConfig):
        NAME = "nested"
        ADDRESS = "default"

    class DefaultConfig(BaseConfig):
        NESTED_CONFIG = NestedConfig()

    config = DefaultConfig()
    config.update(NESTED_CONFIG={"NAME": "updated"})
    config["NESTED_CONFIG.ADDRESS"] = "address"
    >>> config.NESTED_CONFIG.NAME
    updated
    >>> config.NESTED_CONFIG.ADDRESS
    address


Lazy
---------------

Use `lazy` to turn any callable into a lazy evaluated callable. Results are memoized;
the function is evaluated on first access.


.. code-block:: python

    from configalchemy.lazy import lazy, reset_lazy


    def get_name():
        print("evaluating")
        return "World"


    lazy_name = lazy(get_name)
    >>> print(f"Hello {lazy_name}")
    evaluating
    Hello World
    >>> print(f"Hello {lazy_name}")
    Hello World
    >>> reset_lazy(lazy_name)
    >>> print(f"Hello {lazy_name}")
    evaluating
    Hello World

Proxy
------------------

Use `proxy` to turn any callable into a lazy evaluated callable. Results are not memoized;
the function is evaluated on every access.


.. code-block:: python

    from configalchemy.lazy import proxy


    def get_name():
        print("evaluating")
        return "World"


    lazy_name = proxy(get_name)
    >>> print(f"Hello {lazy_name}")
    evaluating
    Hello World
    >>> print(f"Hello {lazy_name}")
    evaluating
    Hello World

Pool
------------------
Use `Pool` to turn any callable into a pool. Result will be return by a context manager.
the function is evaluated on result first access.

.. code-block:: python

    from configalchemy.lazy import Pool


    def connect():
        print("connecting")
        return socket


    connect_pool = Pool(connect)
    >>> with connect_pool as connect:
    ...     connect.send("")
    connecting
    0
    >>> with connect_pool as connect:
    ...     connect.send("")
    0

Access config from Apollo
-------------------------------------------

`Apollo - A reliable configuration management system <https://github.com/ctripcorp/apollo>`_

You can inherit from :any:`ApolloBaseConfig` to access config from Apollo.

.. code-block:: python

    from configalchemy.contrib.apollo import ApolloBaseConfig
    class DefaultConfig(ApolloBaseConfig):

        #: apollo
        ENABLE_LONG_POLL = True
        APOLLO_SERVER_URL = ""
        APOLLO_APP_ID = ""
        APOLLO_CLUSTER = "default"
        APOLLO_NAMESPACE = "application"



