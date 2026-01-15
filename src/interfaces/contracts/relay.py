from typing import Optional
import toml
from src.utils.data_structures import TokenNative, UserNativeData
from src.flow.fee_tracker import FeeTracker
from .contract_client import ContractClient
from src.utils.contracts import get_contract_address

config = toml.load("config.toml")
relay_name = config["contract"]["name"]["relay"]
relay_path = config["contract"]["abi_path"]["relay"]


class Relay(ContractClient):
    def __init__(
            self, 
            token_native: TokenNative,
            sender_data: Optional[UserNativeData]  = None,
            fee_tracker: Optional[FeeTracker]  = None
        ):
        relay_address =  get_contract_address(relay_name, token_native)
        super().__init__(token_native, relay_path, relay_address, sender_data, fee_tracker)

    def get_voting_round_id(self, block: int) -> int:
        timestamp = self.web3.eth.get_block(block)['timestamp']
        round_id = self.read(
            "getVotingRoundId",
            inputs=[timestamp]
        )
        return int(round_id)
