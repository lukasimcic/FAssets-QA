from typing import Optional
from src.interfaces.network.networks.native_networks.native_network import NativeNetwork
from src.utils.data_structures import UserCredentials
from src.flow.fee_tracker import FeeTracker
from src.utils.contracts import get_contract_names
from .contract_client import ContractClient


class AgentVault(ContractClient):
    def __init__(
            self, 
            network: NativeNetwork,
            vault_address: str, 
            sender_data: Optional[UserCredentials]  = None, 
            fee_tracker: Optional[FeeTracker]  = None
        ):
        names = get_contract_names(self)
        super().__init__(names, network, vault_address, sender_data=sender_data, fee_tracker=fee_tracker)

    def collateral_pool(self) -> str:
        return self.read("collateralPool")