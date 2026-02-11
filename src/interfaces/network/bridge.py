from decimal import Decimal
import toml
from typing import Optional
from web3 import Web3
from src.interfaces.contracts.asset_manager import AssetManager
from src.interfaces.contracts.fasset_oft_adapter import FAssetOFTAdapter
from src.interfaces.contracts.fasset import FAsset
from src.flow.fee_tracker import FeeTracker
from src.utils.data_structures import TokenExternalNative, TokenFAsset, TokenNative, TokenUnderlying, UserCredentials
from src.utils.encoding import pad_left_to_64_hex, pad_0x, unpad_0x

config = toml.load("config.toml")
eids = config["network"]["eid"]

# TODO decide if token_native or native_network
class Bridge():
    def __init__(
            self,   
            token_native: TokenNative, 
            token_underlying: TokenUnderlying, 
            user_native_credentials: UserCredentials, 
            fee_tracker: Optional[FeeTracker]  = None
        ):
        self.token_native = token_native
        self.token_underlying = token_underlying
        self.user_native_credentials = user_native_credentials
        self.ft = fee_tracker
        self.token_fasset = TokenFAsset.from_underlying(token_underlying)

    def _approve_tokens(self, spender: str, amount: Decimal, composer: bool = True):
        amount_uba = self.token_fasset.to_uba(amount)
        f = FAsset(self.native_network, self.token_fasset, self.user_native_credentials, self.ft)
        f.approve(spender, amount_uba)
        if composer:
            f.approve(self.token_native.composer_address, amount_uba)
    
    def _get_send_params(self, dst_eid: int, amount_uba: int, options: str) -> dict:
        return {
            "dstEid": dst_eid,
            "to": pad_0x(pad_left_to_64_hex(unpad_0x(self.user_native_credentials.address))),
            "amountLD": amount_uba,
            "minAmountLD": amount_uba,
            "extraOptions": options,
            "composeMsg": "0x",
            "oftCmd": "0x",
        }

    def to_hyperevm_testnet(self, lots: int):
        eid = eids["hyperliquid_testnet"]
        lot_size = AssetManager(self.native_network, self.token_fasset).lot_size()
        amount = Decimal(lots * lot_size)
        foa = FAssetOFTAdapter(
            self.native_network, 
            self.token_fasset, 
            self.user_native_credentials, 
            self.ft
            )
        self._approve_tokens(foa.address, amount)
        amount_uba = self.token_fasset.to_uba(amount)
        options = foa.combine_options(eid)
        send_params = self._get_send_params(eid, amount_uba, options)
        native_fee = foa.quote_native_fee(send_params, False)
        return foa.send(send_params, native_fee, 0, self.user_native_credentials.address)
    
    def from_hyperevm_testnet(self, lots: int):
        eid = eids[self.token_native.name]
        lot_size = AssetManager(self.native_network, self.token_fasset).lot_size()
        amount = Decimal(lots * lot_size)
        foa = FAssetOFTAdapter(
            TokenExternalNative.FtestXRP_hyperevm, 
            self.token_fasset,
            self.user_native_credentials,
            self.ft
            )
        amount_uba = self.token_fasset.to_uba(amount)
        options = foa.combine_options(eid)
        send_params = self._get_send_params(eid, amount_uba, options)
        native_fee = foa.quote_native_fee(send_params, False)
        return foa.send(send_params, native_fee, 0, self.user_native_credentials.address)