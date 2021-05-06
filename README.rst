=============
ConfigAlchemy
=============

.. image:: https://img.shields.io/pypi/v/configalchemy.svg
        :target: https://pypi.python.org/pypi/configalchemy

.. image:: https://github.com/GuangTianLi/configalchemy/workflows/test/badge.svg
        :target: https://github.com/GuangTianLi/configalchemy/actions
        :alt: CI Test Status

.. image:: https://readthedocs.org/projects/configalchemy/badge/?version=latest
        :target: https://configalchemy.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/pypi/pyversions/configalchemy.svg
        :target: https://pypi.org/project/configalchemy/

.. image:: https://codecov.io/gh/GuangTianLi/configalchemy/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/GuangTianLi/configalchemy

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
  :target: https://github.com/psf/black



The Settings and Configuration on ideal practices for app development and package building.


* Free software: MIT license
* Documentation: https://configalchemy.readthedocs.io.

Installation
----------------

.. code-block:: shell

    $ pipenv install configalchemy
    ✨🍰✨

Only **Python 3.6+** is supported.

Example
--------

.. code-block:: python

        from configalchemy import BaseConfig

        class DefaultConfig(BaseConfig):
            NAME = "test"

        config = DefaultConfig()
        config.NAME
        >>> 'test'

Features
----------

- Base on `The Twelve-Factor App Configuration <https://12factor.net/config>`_.
- Configurable dynamic configurator
- Configuration-Oriented Development

    - Define default config value and its type which is used in your project
    - Use class to support inheritance to explicitly define configurable config

- Override config value from multiple source with **priority supported**

    - Callable function return value
    - File (default: json)
    - Environment Variables

- **Proper Typecast** before overriding
- Generic Config Type Support by custom typecast
- Lazy and Proxy Object Support.
- Extension

    - Full `Apollo - A reliable configuration management system <https://github.com/ctripcorp/apollo>`_ Features Support

TODO
-------

- IOC - Injector, Singleton
