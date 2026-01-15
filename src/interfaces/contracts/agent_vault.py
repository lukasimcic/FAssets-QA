from typing import Optional
import toml
from src.utils.data_structures import TokenNative, UserNativeData
from src.flow.fee_tracker import FeeTracker
from .contract_client import ContractClient

config = toml.load(open("config.toml"))
agent_vault_path = config["contract"]["abi_path"]["agent_vault"]


class AgentVault(ContractClient):
    def __init__(
            self, 
            token_native: TokenNative,
            vault_address: str, 
            sender_data: Optional[UserNativeData]  = None, 
            fee_tracker: Optional[FeeTracker]  = None
        ):
        super().__init__(token_native, agent_vault_path, vault_address, sender_data, fee_tracker)

    def collateral_pool(self) -> str:
        return self.read("collateralPool")