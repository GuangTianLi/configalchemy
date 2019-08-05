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

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
  :target: https://github.com/psf/black



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

        class DefaultConfig(BaseConfig):
            TEST = "test"

        config = DefaultConfig()
        config.TEST # attribute style access
        >>> 'test'
        config['TEST'] # dict item style access
        >>> 'test'
        config.get('TEST') # dict get style access
        >>> 'test'
        config.get('HOST', 'local') # Providing defaults
        >>> 'local'

Features
----------

- Configurable dynamic configurator
- Configuration-Oriented Development

    - Define default config value and its type which is used in your project
    - Use class to support inheritance to explicitly define configurable config

- Override config value from multiple source with **priority supported**

    - Callable function return value
    - File (json)
    - Environment Variables

- **Proper Typecast** before overriding
- Generic Config Type Support by custom typecast

- Extension

    - Full `Apollo - A reliable configuration management system <https://github.com/ctripcorp/apollo>`_ Features Support

TODO
-------

- Add More Proper Log
