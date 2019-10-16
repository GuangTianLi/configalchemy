=====
Usage
=====

To use ConfigAlchemy in a project.

.. note:: the config key should be **uppercase**.

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

Enable Config File
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

Enable call Function to Access Config
----------------------------------------------------
Define **CONFIGALCHEMY_ENABLE_FUNCTION** to enable access your config from function return value:

.. code-block:: python

    from configalchemy import BaseConfig, ConfigType


    class DefaultConfig(BaseConfig):
        ENABLE_CONFIG_LIST = True
        TYPE = "base"
        NAME = "base"

        def sync_function(self) -> ConfigType:
            return {"NAME": "sync"}

        async def async_function(self) -> ConfigType:
            return {"TYPE": "async"}


    config = DefaultConfig()

    >>> config['TYPE']
    async
    >>> config['NAME']
    sync


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


Access config from Apollo
==============================================

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
