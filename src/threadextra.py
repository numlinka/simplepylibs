# Licensed under the LGPL 3.0 License.
# simplepylibs by numlinka.
# threadextra

# std
import ctypes
import inspect
import threading

from threading import *
from typing import Union, Type


__name__ = "threadextra"
__author__ = "numlinka"
__license__ = "LGPL 3.0"
__copyright__ = "Copyright (C) 2022 numlinka"

__version_info__ = (1, 0, 2)
__version__ = ".".join(map(str, __version_info__))


class ThreadExtra (Thread):
    def force_stop(self) -> None:
        tid = ctypes.c_long(self.ident)
        exctype = ctypes.py_object(SystemExit)
        result = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, exctype)

        if result == 0:
            raise ValueError("Invalid thread id, why?")
        elif result != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")


def force_stop_thread(thread: Union[int, Thread], exctype: Type[BaseException] = SystemExit) -> None:
    if isinstance(thread, int):
        tid = thread
    elif isinstance(thread, Thread):
        tid = thread.ident
    else:
        raise TypeError("Argument 1 must be int or threading.Thread")

    c_tid = ctypes.c_long(tid)

    if not inspect.isclass(exctype):
        raise TypeError("Argument 2 must be type")
    elif not issubclass(exctype, BaseException):
        raise TypeError("Argument 2 must be subclass of BaseException")

    c_exctype = ctypes.py_object(exctype)

    result = ctypes.pythonapi.PyThreadState_SetAsyncExc(c_tid, c_exctype)

    if result == 0:
        raise ValueError("Invalid thread id")
    elif result != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(c_tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")



__all__ = threading.__all__ + [
    "ThreadExtra",
    "force_stop_thread"
]
