=====
Usage
=====

To use ConfigAlchemy in a project.

.. note:: the config key should be **uppercase**.

.. code-block:: python

    from configalchemy import BaseConfig

    class DefaultObject(BaseConfig):
        TEST = "test"

    config = DefaultObject()

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

    class DefaultObject(BaseConfig):
        CONFIGALCHEMY_CONFIG_FILE = 'test.json' #: etc: {'NAME': 'json'}
        NAME = 'base'

    config = DefaultObject()

    >>> config['NAME']
    json

Enable call Function to Access Config
----------------------------------------------------
Define **CONFIGALCHEMY_ENABLE_FUNCTION** to enable access your config from function return value:

.. code-block:: python

    from configalchemy import BaseConfig

    async def get_config_async(current_config: dict) -> dict:
        return {'TYPE': 'async'}


    def get_config(current_config: dict) -> dict:
        return {'NAME': 'sync'}

    class DefaultObject(BaseConfig):
        ENABLE_CONFIG_LIST = True
        TYPE = 'base'
        NAME = 'base'


    config = DefaultObject(
        function_list=[get_config],
        coroutine_function_list=[get_config_async])

    >>> config['TYPE']
    async
    >>> config['NAME']
    sync


