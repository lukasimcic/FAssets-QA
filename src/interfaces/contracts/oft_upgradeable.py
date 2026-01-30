from decimal import Decimal
from typing import Optional
from src.interfaces.network.bridge import bridged_address
from src.utils.data_structures import TokenBridged, UserNativeData
from src.flow.fee_tracker import FeeTracker
from .contract_client import ContractClient
from src.utils.contracts import get_contract_names


class OFTUpgradeable(ContractClient):
    def __init__(
            self,
            token_bridged: TokenBridged,
            sender_data: Optional[UserNativeData] = None,
            fee_tracker: Optional[FeeTracker] = None
        ):
        self.token_fasset = token_bridged.token_fasset
        names = get_contract_names(self, self.token_fasset.token_underlying)
        super().__init__(names, token_bridged, sender_data=sender_data, fee_tracker=fee_tracker)

    def get_balance(self) -> Decimal:
        balance_uba = self.read("balanceOf", [bridged_address(self.sender_address)])
        return self.token_fasset.from_uba(balance_uba)
    