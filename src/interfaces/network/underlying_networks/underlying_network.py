from src.utils.data_structures import UserUnderlyingData
from src.utils.fee_tracker import FeeTracker
from abc import ABC, abstractmethod



class UnderlyingBaseNetwork(ABC):
    def __init__(self, fee_tracker: FeeTracker | None = None):
        self.fee_tracker = fee_tracker

    @abstractmethod
    def send_transaction(self, target, value):
        """
        Sends transaction to the target address with the specified value.
        Returns a dictionary including transaction hash and amount spent.
        """
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
    def __new__(cls, token, underlying_data : UserUnderlyingData | None = None, fee_tracker=None):
        """
        Factory method to create an instance of the appropriate network class.
        Must be initialized with the  token type, but other parameters depend on the specific network.
        """
        if token == "testXRP":
            from src.interfaces.network.underlying_networks.testXRP import TestXRP
            return TestXRP(
                underlying_data.public_key if underlying_data else None, 
                underlying_data.private_key if underlying_data else None,
                fee_tracker=fee_tracker
            )
        else:
            raise ValueError(f"Unsupported  token: {token}")


