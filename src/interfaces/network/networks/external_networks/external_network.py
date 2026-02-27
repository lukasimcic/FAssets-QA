from decimal import Decimal
from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING
import toml
from src.interfaces.network.networks.network import Network
if TYPE_CHECKING:
    from src.interfaces.network.tokens import TokenExternalFAsset, TokenExternalNative

config = toml.load(Path("config.toml"))
contracts_file = config["file"]["contract_addresses"]
rpc_url = config["network"]["rpc_url"]
eid = config["network"]["eid"]
composer_address = config["network"]["composer_address"]


class ExternalNetwork(Network):
    evm = True

    @classmethod
    def rpc_url(cls) -> str:
        return rpc_url[cls.__name__] if getattr(cls, "evm") else None
    
    @classmethod
    def contracts_file(cls) -> str:
        return contracts_file[cls.__name__] if getattr(cls, "evm") else None
    
    @classmethod
    def eid(cls) -> int:
        return eid[cls.__name__] if getattr(cls, "evm") else None
    
    @classmethod
    def composer_address(cls) -> str:
        return composer_address[cls.__name__] if getattr(cls, "evm") else None

    @abstractmethod
    def get_balance(self, token: "TokenExternalNative | TokenExternalFAsset") -> Decimal:
        pass