from .contract_client import ContractClient
from src.utils.contracts import get_contract_address, get_output_index
from src.utils.config import asset_manager_path, asset_manager_instance_name, my_agent_vault

class AssetManager(ContractClient):
    def __init__(self):
        asset_manager_address =  get_contract_address(asset_manager_instance_name)
        super().__init__(asset_manager_path, asset_manager_address)

    def test(self):
        agent_info = self.contract.functions.getAgentInfo(my_agent_vault).call()
        print(agent_info)

    def collateralPoolTokenTimelockSeconds(self):
        settings = self.contract.functions.getSettings().call()
        idx = get_output_index(self.path, "getSettings", "collateralPoolTokenTimelockSeconds")
        return settings[idx]