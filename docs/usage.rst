=====
Usage
=====

To use ConfigAlchemy in a project.

.. code-block:: python

    from configalchemy import BaseConfig

    class DefaultObject(BaseConfig):
        TEST = "test"

    config = DefaultObject()
