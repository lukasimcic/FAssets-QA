from abc import ABC, abstractmethod


class UnderlyingBaseNetwork(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def send_transaction(self, target, value):
        pass

    @abstractmethod
    def get_balance(self):
        pass

    @abstractmethod
    def get_current_block(self):
        pass

    @abstractmethod
    def get_block_of_tx(self, tx_hash):
        pass


class UnderlyingNetwork:
    def __new__(cls, token, underlying_data):
        """
        Factory method to create an instance of the appropriate network class.
        Must be initialized with the  token type, but other parameters depend on the specific network.
        """
        if token == "testXRP":
            from src.interfaces.network.underlying_networks.testXRP import TestXRP
            return TestXRP(underlying_data["public_key"], underlying_data["private_key"])
        else:
            raise ValueError(f"Unsupported  token: {token}")


