from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from .contract_client import ContractClient
from src.utils.contracts import get_contract_names
if TYPE_CHECKING: 
    from src.interfaces.network.networks.external_networks.external_network import ExternalNetwork
    from src.interfaces.network.tokens import TokenFAsset
    from src.utils.data_structures import UserCredentials
    from src.flow.fee_tracker import FeeTracker


class OFTUpgradeable(ContractClient):
    def __init__(
            self,
            network: "ExternalNetwork",
            token_fasset: "TokenFAsset",
            sender_credentials: Optional["UserCredentials"] = None,
            fee_tracker: Optional["FeeTracker"] = None
        ):
        self.token_fasset = token_fasset
        names = get_contract_names(self, token_fasset)
        super().__init__(names, network, sender_credentials=sender_credentials, fee_tracker=fee_tracker)

    def get_balance(self) -> Decimal:
        balance_uba = self.read("balanceOf", [self.sender_address])
        return self.token_fasset.from_uba(balance_uba)
    