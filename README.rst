=============
ConfigAlchemy
=============

.. image:: https://img.shields.io/pypi/v/configalchemy.svg
        :target: https://pypi.python.org/pypi/configalchemy

.. image:: https://img.shields.io/travis/GuangTianLi/configalchemy.svg
        :target: https://travis-ci.org/GuangTianLi/configalchemy

.. image:: https://readthedocs.org/projects/configalchemy/badge/?version=latest
        :target: https://configalchemy.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/pypi/pyversions/configalchemy.svg
        :target: https://pypi.org/project/configalchemy/

.. image:: https://codecov.io/gh/GuangTianLi/configalchemy/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/GuangTianLi/configalchemy



The Settings and Configuration on ideal practices for app development.


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

        class DefaultObject(BaseConfig):
            TEST = "test"

        config = DefaultObject()
        print(config.TEST) # attribute style access
        print(config['TEST']) # dict item style access
        print(config.get('TEST')) # dict get style access
        print(config.get('HOST', 'local')) # Providing defaults

Features
----------

- Configurable Dynamic configurator
- Configuration-Oriented Development

    - Define default config value and its type which is used in your project
    - Use class to support inheritance to explicitly define configurable config

- override config value from multiple source with **priority supported**

    - Callable function return value
    - File (json)
    - Environment Variables

- **Force typecast** before overriding
- Inherit from typing.MutableMapping

- Extension

    - Full `Apollo - A reliable configuration management system <https://github.com/ctripcorp/apollo>`_ Features Support

TODO
-------

* Complex Config Type Support
