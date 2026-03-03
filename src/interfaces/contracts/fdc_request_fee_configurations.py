from typing import Optional, TYPE_CHECKING
from .contract_client import ContractClient
from src.utils.contracts import get_contract_names
if TYPE_CHECKING:
    from src.interfaces.network.networks.native_networks.native_network import NativeNetwork
    from src.utils.data_structures import UserCredentials
    from src.flow.fee_tracker import FeeTracker


class FdcRequestFeeConfigurations(ContractClient):
    def __init__(
            self, 
            network: "NativeNetwork",
            sender_credentials: Optional["UserCredentials"]  = None,
            fee_tracker: Optional["FeeTracker"]  = None
        ):
        names = get_contract_names(self)
        super().__init__(names, network, sender_credentials=sender_credentials, fee_tracker=fee_tracker)

    def get_request_fee(self, data: bytes) -> int:
        required_fee = self.read(
            "getRequestFee",
            inputs=[data]
        )
        return required_fee
