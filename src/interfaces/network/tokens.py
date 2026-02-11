from pathlib import Path
from enum import Enum
import toml
from typing import Type, Union, TYPE_CHECKING
from decimal import Decimal
from src.interfaces.network.networks.underlying_networks.XRPL_testnet import XRPL_testnet
from src.interfaces.network.networks.native_networks.Coston2 import Coston2
from src.interfaces.network.networks.external_networks.HyperEVM_testnet import HyperEVM_testnet
from src.interfaces.network.networks.external_networks.HyperCore_testnet import HyperCore_testnet
if TYPE_CHECKING:
    from src.interfaces.network.networks.external_networks.external_network import ExternalNetwork
    from src.interfaces.network.networks.native_networks.native_network import NativeNetwork
    from src.interfaces.network.networks.underlying_networks.underlying_network import UnderlyingNetwork

config = toml.load(Path("config.toml"))
contracts_file = config["file"]["contract_addresses"]
rpc_url = config["network"]["rpc_url"]
faucet_url = config["network"]["faucet_url"]
fdc_url = config["network"]["fdc_url"]
da_url = config["network"]["da_url"]
zero_address = config["network"]["zero_address"]
composer_address = config["network"]["composer_address"]


class UbaMixin:
    def to_uba(self, amount: Decimal) -> int:
        return int(amount * 10 ** self.decimals)
    def from_uba(self, amount_uba: int) -> Decimal:
        return Decimal(amount_uba) / Decimal(10) ** self.decimals

class TokenNative(UbaMixin, Enum):
    C2FLR = (Coston2, 18)
    def __init__(self, network: Type["NativeNetwork"], decimals: int):
        self.network = network
        self.decimals = decimals
        self.compare_tolerance = 10 ** (-decimals + 6)

class TokenUnderlying(UbaMixin, Enum):
    testXRP = (XRPL_testnet, 6)
    def __init__(self, network: Type["UnderlyingNetwork"], decimals: int):
        self.network = network
        self.decimals = decimals
        self.compare_tolerance = 10 ** (-decimals + 1)

class TokenFAsset(UbaMixin, Enum):
    FTestXRP = (TokenUnderlying.testXRP)
    def __init__(self, token_underlying: TokenUnderlying):
        self.token_underlying = token_underlying
        self.decimals = token_underlying.decimals
        self.compare_tolerance = 10 ** -self.decimals
    @classmethod
    def from_underlying(cls, underlying: TokenUnderlying):
        name = underlying.name
        name_capitalized = name[:1].upper() + name[1:]
        fasset_name = f"F{name_capitalized}"
        return cls[fasset_name]

class TokenExternalNative(UbaMixin, Enum):
    HYPE_HyperEVM_testnet = (HyperEVM_testnet, 18)
    HYPE_HyperCore_testnet = (HyperCore_testnet, 18)
    def __init__(self, network: Type["ExternalNetwork"], decimals: int):
        self.network = network
        self.decimals = decimals
        self.compare_tolerance = 10 ** (-self.decimals + 6)

class TokenExternalFAsset(UbaMixin, Enum):
    FTestXRP_HyperEVM_testnet = (TokenFAsset.FTestXRP, HyperEVM_testnet)
    FTestXRP_HyperCore_testnet = (TokenFAsset.FTestXRP, HyperCore_testnet)
    def __init__(self, token_fasset: TokenFAsset, network: Type["ExternalNetwork"]):
        self.network = network
        self.token_fasset = token_fasset
        self.decimals = token_fasset.decimals
        self.compare_tolerance = 10 ** -self.decimals
    @classmethod
    def from_fasset(cls, fasset: TokenFAsset, network: Type["ExternalNetwork"]):
        name = f"{fasset.name}_{network().name}"
        return cls[name]

Token = Union[TokenNative, TokenUnderlying, TokenFAsset, TokenExternalNative, TokenExternalFAsset]
Coin = Union[TokenNative, TokenUnderlying, TokenExternalNative]

COIN_DICT : dict[Type["NativeNetwork"] | Type["UnderlyingNetwork"] | Type["ExternalNetwork"], Coin] = {
    Coston2: TokenNative.C2FLR,
    XRPL_testnet: TokenUnderlying.testXRP,
    HyperEVM_testnet: TokenExternalNative.HYPE_HyperEVM_testnet,
    HyperCore_testnet: TokenExternalNative.HYPE_HyperCore_testnet
}
