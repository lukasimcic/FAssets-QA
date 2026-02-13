from typing import TYPE_CHECKING, Optional
from src.utils.contracts import get_contract_names
from .contract_client import ContractClient
if TYPE_CHECKING:
    from src.interfaces.network.networks.native_networks.native_network import NativeNetwork
    from src.utils.data_structures import UserCredentials
    from src.flow.fee_tracker import FeeTracker


class AgentVault(ContractClient):
    def __init__(
            self, 
            network: "NativeNetwork",
            vault_address: str, 
            sender_credentials: Optional["UserCredentials"]  = None, 
            fee_tracker: Optional["FeeTracker"]  = None
        ):
        names = get_contract_names(self)
        super().__init__(names, network, vault_address, sender_credentials=sender_credentials, fee_tracker=fee_tracker)

    def collateral_pool(self) -> str:
        return self.read("collateralPool")