import inspect
from collections.abc import Hashable
from functools import wraps
from typing import TypeVar

_T = TypeVar("T")


def singleton(cls: type[_T]) -> type[_T]:
    new = cls.__new__
    init = cls.__init__
    init_sig = inspect.signature(cls.__init__)
    new_sig = init_sig

    @wraps(cls.__new__)
    def __new__(cls, *args, **kwargs):
        bound = new_sig.bind(cls, *args, **kwargs)
        bound.apply_defaults()
        key = tuple()
        for val in bound.arguments.values():
            if val is cls:  # 移除第一个参数cls
                continue
            if isinstance(val, Hashable):
                key += (val,)
        if key not in cls._instances:
            cls._instances[key] = new(cls)
        return cls._instances[key]

    @wraps(cls.__init__)
    def __init__(self, *args, **kwargs):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        return init(self, *args, **kwargs)

    cls._instances = {}
    cls.__new__ = __new__
    cls.__init__ = __init__
    return cls
