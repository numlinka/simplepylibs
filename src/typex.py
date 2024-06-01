# Licensed under the LGPL 3.0 License.
# simplepylibs by numlinka.
# typex

# std
from abc import *
from types import *
from typing import *


__name__ = "typex"
__author__ = "numlinka"
__license__ = "LGPL 3.0"
__copyright__ = "Copyright (C) 2022 numlinka"

__version_info__ = (0, 1, 3)
__version__ = ".".join(map(str, __version_info__))


class static (object):
    def __new__(cls):
        raise TypeError("Cannot instantiate static class.")


class abstract (ABC):
    abstractmethod


class singleton (object):
    """## Singleton class.

    A singleton class is a class that can only be instantiated once,
    The __init__ is called only once.
    """

    _singleton_instance: Self
    _singleton_init_method: MethodType
    _singleton_initialized: bool

    def __new__(cls, *args, **kwargs) -> Self:
        if cls is singleton:
            raise TypeError("Cannot instantiate base singleton class.")
        if not hasattr(cls, "_singleton_instance"):
            cls._singleton_init_method = cls.__init__
            cls.__init__ = singleton.__init__
            cls._singleton_instance = super(singleton, cls).__new__(cls)
        return cls._singleton_instance

    def __init__(self, *args, **kwargs) -> None:
        cls = self.__class__
        if not hasattr(cls, "_singleton_initialized") or not cls._singleton_initialized:
            cls._singleton_initialized = True
            self._singleton_init_method(*args, **kwargs)


__all__ = [
    "static",
    "abstract",
    "abstractmethod",
    "singleton"
]
