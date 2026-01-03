from src.utils.data_structures import TokenNative, UserNativeData
from src.flow.fee_tracker import FeeTracker
from .contract_client import ContractClient
from config.config_qa import agent_vault_path


class AgentVault(ContractClient):
    def __init__(
            self, 
            token_native: TokenNative,
            vault_address: str, 
            sender_data: UserNativeData | None = None, 
            fee_tracker: FeeTracker | None = None
        ):
        super().__init__(token_native, agent_vault_path, vault_address, sender_data, fee_tracker)

    def collateral_pool(self) -> str:
        return self.read("collateralPool")