from decimal import Decimal
from typing import Optional
from src.interfaces.network.tokens import TokenFAsset
from src.interfaces.network.networks.native_networks.native_network import NativeNetwork
from src.utils.data_structures import UserCredentials
from src.flow.fee_tracker import FeeTracker
from .contract_client import ContractClient
from src.utils.contracts import get_contract_names


class FAsset(ContractClient):
    def __init__(
            self, 
            network: NativeNetwork,
            token_fasset: TokenFAsset,
            sender_data: Optional[UserCredentials] = None,
            fee_tracker: Optional[FeeTracker] = None
        ):
        self.token_fasset = token_fasset
        names = get_contract_names(self, token_fasset)
        super().__init__(names, network, sender_data=sender_data, fee_tracker=fee_tracker)

    def get_balance(self) -> Decimal:
        return self.balance_of(self.sender_address)

    def balance_of(self, address: str) -> Decimal:
        balance_uba = self.read("balanceOf", inputs=[address])
        return self.token_fasset.from_uba(balance_uba)
    
    def approve(self, spender: str, amount: int):
        return self.write("approve", inputs=[spender, amount])
    
    def allowance(self, owner: str, spender: str) -> int:
        return self.read("allowance", inputs=[owner, spender])