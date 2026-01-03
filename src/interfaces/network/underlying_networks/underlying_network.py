from decimal import Decimal
from abc import ABC, abstractmethod

from src.utils.data_structures import TokenUnderlying, UserUnderlyingData
from src.flow.fee_tracker import FeeTracker


class UnderlyingBaseNetwork(ABC):
    def __init__(self, fee_tracker: FeeTracker | None = None):
        self.fee_tracker = fee_tracker

    @abstractmethod
    def send_transaction(self, target: str, value: Decimal) -> dict:
        """
        Sends transaction to the target address with the specified value.
        Returns a dictionary including transaction hash and amount spent.
        """
        pass

    @abstractmethod
    def get_balance(self) -> Decimal:
        pass

    @abstractmethod
    def get_current_block(self) -> int:
        pass

    @abstractmethod
    def get_block_of_tx(self, tx_hash: str) -> int:
        pass

    @abstractmethod
    def generate_new_address(self) -> dict:
        pass

    @abstractmethod
    def request_funds(self) -> int:
        pass

class UnderlyingNetwork:
    def __new__(cls, token: TokenUnderlying, underlying_data : UserUnderlyingData | None = None, fee_tracker: FeeTracker | None = None):
        """
        Factory method to create an instance of the appropriate network class.
        Must be initialized with the token type, but other parameters depend on the specific network.
        """
        if token == TokenUnderlying.testXRP:
            from src.interfaces.network.underlying_networks.testXRP import TestXRP
            return TestXRP(
                underlying_data.public_key if underlying_data else None, 
                underlying_data.private_key if underlying_data else None,
                fee_tracker=fee_tracker
            )


