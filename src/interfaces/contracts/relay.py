from typing import Optional
from src.interfaces.network.networks.native_networks.native_network import NativeNetwork
from src.utils.data_structures import UserCredentials
from src.flow.fee_tracker import FeeTracker
from .contract_client import ContractClient
from src.utils.contracts import get_contract_names


class Relay(ContractClient):
    def __init__(
            self, 
            network: NativeNetwork,
            sender_data: Optional[UserCredentials]  = None,
            fee_tracker: Optional[FeeTracker]  = None
        ):
        names = get_contract_names(self)
        super().__init__(names, network, sender_data=sender_data, fee_tracker=fee_tracker)

    def get_voting_round_id(self, block: int) -> int:
        timestamp = self.web3.eth.get_block(block)['timestamp']
        round_id = self.read(
            "getVotingRoundId",
            inputs=[timestamp]
        )
        return int(round_id)
