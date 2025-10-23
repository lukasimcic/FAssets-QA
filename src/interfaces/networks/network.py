from abc import ABC, abstractmethod


class BaseNetwork(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def send_transaction(self, target, value):
        pass

    @abstractmethod
    def get_balance(self):
        pass


class Network:
    def __new__(cls, token, *args, **kwargs):
        """
        Factory method to create an instance of the appropriate network class.
        Must be initialized with the  token type, but other parameters depend on the specific network.
        """
        if token == "testXRP":
            from src.interfaces.networks.testXRP import TestXRP
            return TestXRP(*args, **kwargs)
        if token == "C2FLR":
            from src.interfaces.networks.c2flr import C2FLR
            return C2FLR(*args, **kwargs)
        else:
            raise ValueError(f"Unsupported  token: {token}")


