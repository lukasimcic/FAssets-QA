from decimal import Decimal
from abc import ABC, abstractmethod
from typing import Optional
from src.utils.data_structures import TokenNative, UserNativeData


class NativeBaseNetwork(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_balance(self) -> Decimal:
        pass

    @abstractmethod
    def send_transaction(self, to_address: str, amount: Decimal) -> dict:
        pass

    @abstractmethod
    def get_current_timestamp(self) -> int:
        pass

    @abstractmethod
    def generate_new_address(self) -> dict:
        pass

    @abstractmethod
    def request_funds(self) -> int:
        pass

class NativeNetwork:
    def __new__(cls, token: TokenNative, native_data : Optional[UserNativeData]  = None):
        """
        Factory method to create an instance of the appropriate network class.
        Must be initialized with the  token type, but other parameters depend on the specific network.
        """
        if token == TokenNative.C2FLR:
            from src.interfaces.network.native_networks.c2flr import C2FLR
            return C2FLR(
                native_data.address if native_data else None,
                native_data.private_key if native_data else None
                )


