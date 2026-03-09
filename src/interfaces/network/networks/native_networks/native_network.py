from decimal import Decimal
from abc import abstractmethod
import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional
import time
from dotenv import load_dotenv
import toml
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from src.interfaces.contracts.fasset_oft_adapter import FAssetOFTAdapter
from src.interfaces.network.networks.network import Network
from src.interfaces.contracts.fasset import FAsset
from src.utils.encoding import pad_left_to_64_hex, pad_0x, unpad_0x
if TYPE_CHECKING:
    from src.interfaces.network.tokens import TokenFAsset, TokenNative
    from src.utils.data_structures import UserCredentials

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
    def __init__(self, credentials: Optional["UserCredentials"] = None):
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url()))
        self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        if credentials:
            self.credentials = credentials
            self.address = credentials.address
            self.private_key = credentials.private_key

    @classmethod
    def rpc_url(cls) -> str:
        return rpc_url[cls.__name__]
    
    @classmethod
    def faucet_url(cls) -> str:
        return faucet_url[cls.__name__]

    @classmethod
    def contracts_file(cls) -> str:
        return contracts_file[cls.__name__]

    @classmethod
    def fdc_url(cls) -> str:
        return fdc_url[cls.__name__]

    @classmethod
    def da_url(cls) -> str:
        return da_url[cls.__name__]

    @classmethod
    def zero_address(cls) -> str:
        return zero_address[cls.__name__]

    @classmethod
    def composer_address(cls) -> str:
        return composer_address[cls.__name__]
    
    @classmethod
    def eid(cls) -> int:
        return eid[cls.__name__]

    def get_balance(self, token: "TokenNative | TokenFAsset") -> int:
        from src.interfaces.network.tokens import TokenNative, TokenFAsset
        if isinstance(token, TokenNative):
            if token.network != type(self):
                raise ValueError(f"Token {token.name} does not belong to network {type(self).__name__}.")
            balance_uba = self.web3.eth.get_balance(self.address)
            balance = self.web3.from_wei(balance_uba, 'ether')
        elif isinstance(token, TokenFAsset):
            f = FAsset(
                    self,
                    token,
                    self.credentials
                )
            balance = f.get_balance()
        return balance

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

    def prepare_for_bridge(
            self, 
            to_eid: int, 
            to_address: str, 
            token_fasset: "TokenFAsset",
            amount_uba: int
            ) -> dict:
        foa = FAssetOFTAdapter(
            self, 
            token_fasset, 
            self.credentials
            )
        # approve tokens for bridge
        f = FAsset(self, token_fasset, self.credentials, self.ft)
        f.approve(foa.address, amount_uba)
        f.approve(self.composer_address(), amount_uba)
        # prepare send params
        send_params = {
            "dstEid": to_eid,
            "to": pad_0x(pad_left_to_64_hex(unpad_0x(to_address))),
            "amountLD": amount_uba,
            "minAmountLD": amount_uba,
            "extraOptions": foa.combine_options(to_eid),
            "composeMsg": "0x",
            "oftCmd": "0x",
        }
        return send_params