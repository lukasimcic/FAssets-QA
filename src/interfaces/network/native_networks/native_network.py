from abc import ABC, abstractmethod


class NativeBaseNetwork(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_balance(self):
        pass

    @abstractmethod
    def get_current_timestamp(self):
        pass


class NativeNetwork:
    def __new__(cls, token, native_data):
        """
        Factory method to create an instance of the appropriate network class.
        Must be initialized with the  token type, but other parameters depend on the specific network.
        """
        if token == "C2FLR":
            from src.interfaces.network.native_networks.c2flr import C2FLR
            return C2FLR(native_data["address"], native_data["private_key"])
        else:
            raise ValueError(f"Unsupported  token: {token}")


