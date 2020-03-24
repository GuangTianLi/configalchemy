import io
import os.path
import sys
import traceback
from importlib import import_module
from typing import Any, Optional

currentframe = lambda: sys._getframe(2)

_srcfile = os.path.normcase(__file__)


def import_reference(reference: str) -> Any:
    module_path, class_name = reference.rsplit(".", 1)
    backend_cls = getattr(import_module(module_path), class_name)
    return backend_cls


def find_caller() -> Optional[str]:
    f = currentframe()
    stack_info = None
    while hasattr(f, "f_code"):
        co = f.f_code
        filename = os.path.normcase(co.co_filename)
        if filename == _srcfile:
            if f.f_back:
                f = f.f_back
                continue
        sio = io.StringIO()
        sio.write("Stack (most recent call last):\n")
        traceback.print_stack(f, file=sio)
        stack_info = sio.getvalue()
        if stack_info[-1] == "\n":
            stack_info = stack_info[:-1]
        sio.close()
        break
    return stack_info
