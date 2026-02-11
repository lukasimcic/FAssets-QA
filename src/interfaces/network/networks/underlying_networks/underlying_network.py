from decimal import Decimal
from abc import abstractmethod
from pathlib import Path
from typing import Optional
from requests import Response
import toml
from src.interfaces.network.networks.network import Network
from src.flow.fee_tracker import FeeTracker

config = toml.load(Path("config.toml"))
rpc_url = config["network"]["rpc_url"]
faucet_url = config["network"]["faucet_url"]


class UnderlyingNetwork(Network):
    def __init__(self, fee_tracker: Optional[FeeTracker]  = None):
        self.fee_tracker = fee_tracker

    @classmethod
    def rpc_url(cls):
        return rpc_url[cls.__name__]
    
    @classmethod
    def faucet_url(cls):
        return faucet_url[cls.__name__]

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

    @abstractmethod
    def block_all_deposits(self) -> Response:
        pass

    @abstractmethod
    def unblock_all_deposits(self) -> Response:
        pass