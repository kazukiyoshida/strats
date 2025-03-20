from dataclasses import dataclass


def singletondataclass(cls):
    cls = dataclass(cls)
    original_init = cls.__init__
    cls._instance = None

    def singleton_init(self, *args, **kwargs):
        if not getattr(self, "_initialized", False):
            original_init(self, *args, **kwargs)
            self._initialized = True

    def singleton_new(cls_, *args, **kwargs):
        if cls_._instance is None:
            cls_._instance = object.__new__(cls_)
        return cls_._instance

    cls.__new__ = singleton_new
    cls.__init__ = singleton_init

    return cls
