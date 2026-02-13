from typing import Optional, TYPE_CHECKING
from .contract_client import ContractClient
from src.utils.contracts import get_contract_names
if TYPE_CHECKING:
    from src.interfaces.network.networks.native_networks.native_network import NativeNetwork
    from src.utils.data_structures import UserCredentials
    from src.flow.fee_tracker import FeeTracker
    from src.interfaces.network.tokens import TokenFAsset


class AssetManagerController(ContractClient):
    def __init__(
            self, 
            network: "NativeNetwork",
            token_fasset: "TokenFAsset", 
            sender_credentials: Optional["UserCredentials"]  = None, 
            fee_tracker: Optional["FeeTracker"]  = None
        ):
        names = get_contract_names(self, token_fasset)
        super().__init__(names, network, sender_credentials=sender_credentials, fee_tracker=fee_tracker)
