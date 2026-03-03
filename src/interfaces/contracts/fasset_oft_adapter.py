from typing import Optional, TYPE_CHECKING
from .contract_client import ContractClient
from src.utils.contracts import get_contract_names
if TYPE_CHECKING:
    from src.interfaces.network.networks.external_networks.external_network import ExternalNetwork
    from src.interfaces.network.networks.native_networks.native_network import NativeNetwork
    from src.utils.data_structures import UserCredentials
    from src.interfaces.network.tokens import TokenFAsset
    from src.flow.fee_tracker import FeeTracker



class FAssetOFTAdapter(ContractClient):
    def __init__(
            self,
            network: "NativeNetwork | ExternalNetwork",
            token_fasset: "TokenFAsset",
            sender_credentials: Optional["UserCredentials"] = None,
            fee_tracker: Optional["FeeTracker"] = None
        ):
        names = get_contract_names(self, token_fasset)
        super().__init__(names, network, sender_credentials=sender_credentials, fee_tracker=fee_tracker)

    def combine_options(self, dst_eid: int, msg_type: int = 1, extra_options: str = "0x") -> bytes:
        return self.read("combineOptions", inputs=[dst_eid, msg_type, extra_options])

    def quote_fee(self, send_params: dict, pay_in_lz_token: bool) -> int:
        return self.read("quoteSend", inputs=[send_params, pay_in_lz_token])[0]
    
    def send(self, send_params: dict, native_fee: int, lz_token_fee: int, refund_address: str) -> dict:
        return self.write(
            "send", 
            inputs=[send_params, {"nativeFee": native_fee, "lzTokenFee": lz_token_fee}, refund_address],
            value=native_fee
            )