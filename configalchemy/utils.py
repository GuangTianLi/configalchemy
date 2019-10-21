from importlib import import_module
from typing import Any


def import_reference(reference: str) -> Any:
    module_path, class_name = reference.rsplit(".", 1)
    backend_cls = getattr(import_module(module_path), class_name)
    return backend_cls
