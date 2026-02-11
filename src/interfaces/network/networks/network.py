from abc import ABC

class classproperty(property):
    def __get__(self, obj, cls):
        return self.fget(cls)

class Network(ABC):
    @classproperty
    def coin(cls):
        from src.interfaces.network.tokens import COIN_DICT
        return COIN_DICT[cls]