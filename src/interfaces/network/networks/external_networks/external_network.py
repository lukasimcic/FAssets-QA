from decimal import Decimal
from abc import abstractmethod
from pathlib import Path
import toml
from src.interfaces.network.networks.network import Network

config = toml.load(Path("config.toml"))
contracts_file = config["file"]["contract_addresses"]
rpc_url = config["network"]["rpc_url"]


class ExternalNetwork(Network):
    def __init__(self, evm: bool = True):
        self.evm = evm

    @classmethod
    def rpc_url(cls):
        return rpc_url[cls.__name__]
    
    @classmethod
    def contracts_file(cls):
        return contracts_file[cls.__name__]

    @abstractmethod
    def get_balance(self) -> Decimal:
        pass