from decimal import Decimal
from abc import abstractmethod
from pathlib import Path
import toml
from src.interfaces.network.networks.network import Network

config = toml.load(Path("config.toml"))
contracts_file : dict[str, str] = config["file"]["contract_addresses"]
rpc_url : dict[str, str] = config["network"]["rpc_url"]
faucet_url : dict[str, str] = config["network"]["faucet_url"]
fdc_url : dict[str, str] = config["network"]["fdc_url"]
da_url : dict[str, str] = config["network"]["da_url"]
zero_address : dict[str, str] = config["network"]["zero_address"]
composer_address : dict[str, str] = config["network"]["composer_address"]
eid : dict[str, int] = config["network"]["eid"]


class NativeNetwork(Network):

    @classmethod
    def rpc_url(cls):
        return rpc_url[cls.__name__]
    
    @classmethod
    def faucet_url(cls):
        return faucet_url[cls.__name__]

    @classmethod
    def contracts_file(cls):
        return contracts_file[cls.__name__]

    @classmethod
    def fdc_url(cls):
        return fdc_url[cls.__name__]

    @classmethod
    def da_url(cls):
        return da_url[cls.__name__]

    @classmethod
    def zero_address(cls):
        return zero_address[cls.__name__]

    @classmethod
    def composer_address(cls):
        return composer_address[cls.__name__]
    
    @classmethod
    def eid(cls):
        return eid[cls.__name__]

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