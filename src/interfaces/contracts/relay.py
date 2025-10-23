from .contract_client import ContractClient
from src.utils.contracts import get_contract_address
from src.utils.config import relay_path, relay_instance_name

class Relay(ContractClient):
    def __init__(self, sender_address, sender_private_key):
        relay_address =  get_contract_address(relay_instance_name)
        super().__init__(sender_address, sender_private_key, relay_path, relay_address)

    def get_voting_round_id(self, block):
        timestamp = self.web3.eth.get_block(block)['timestamp']
        round_id = self.read(
            "getVotingRoundId",
            inputs=[timestamp]
        )
        return int(round_id)
