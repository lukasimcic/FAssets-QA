from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from src.interfaces.contracts.asset_manager import AssetManager
from src.interfaces.contracts.fasset_oft_adapter import FAssetOFTAdapter
from src.utils.encoding import pad_left_to_64_hex, pad_0x, unpad_0x
if TYPE_CHECKING:
    from src.interfaces.network.networks.external_networks.external_network import ExternalNetwork
    from src.interfaces.network.networks.native_networks.native_network import NativeNetwork
    from src.interfaces.contracts.fasset import FAsset
    from src.utils.data_structures import UserCredentials
    from src.interfaces.network.tokens import TokenFAsset
    from src.flow.fee_tracker import FeeTracker


class Bridge():
    def __init__(
            self,
            native_network: "NativeNetwork", 
            token_fasset: "TokenFAsset", 
            user_native_credentials: "UserCredentials", 
            fee_tracker: Optional["FeeTracker"]  = None
        ):
        self.native_network = native_network
        self.token_fasset = token_fasset
        self.credentials = user_native_credentials
        self.ft = fee_tracker

    def _approve_tokens(self, spender: str, amount: Decimal, composer: bool = True):
        amount_uba = self.token_fasset.to_uba(amount)
        f = FAsset(self.native_network, self.token_fasset, self.credentials, self.ft)
        f.approve(spender, amount_uba)
        if composer:
            f.approve(self.native_network.composer_address(), amount_uba)
    
    def _get_send_params(self, dst_eid: int, amount_uba: int, options: str) -> dict:
        return {
            "dstEid": dst_eid,
            "to": pad_0x(pad_left_to_64_hex(unpad_0x(self.credentials.address))),
            "amountLD": amount_uba,
            "minAmountLD": amount_uba,
            "extraOptions": options,
            "composeMsg": "0x",
            "oftCmd": "0x",
        }

    def bridge(
            self, 
            from_network: "NativeNetwork | ExternalNetwork", 
            to_network: "NativeNetwork | ExternalNetwork", 
            lots: int
        ):
        lot_size = AssetManager(self.native_network, self.token_fasset).lot_size()
        amount = Decimal(lots * lot_size)
        foa = FAssetOFTAdapter(
            from_network, 
            self.token_fasset, 
            self.credentials, 
            self.ft
            )
        self._approve_tokens(foa.address, amount)
        amount_uba = self.token_fasset.to_uba(amount)
        to_eid = to_network.eid()
        options = foa.combine_options(to_eid)
        send_params = self._get_send_params(to_eid, amount_uba, options)
        native_fee = foa.quote_native_fee(send_params, False)
        self.ft.other_fees[from_network.coin] += native_fee
        return foa.send(send_params, native_fee, 0, self.credentials.address)