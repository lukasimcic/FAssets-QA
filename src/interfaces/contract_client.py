from utils.config import rpc_url, coston2_contracts, asset_manager_name, asset_manager_abi, my_agent_vault
from web3 import Web3

class ContractClient:
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        assert self.web3.is_connected()

    @staticmethod
    def get_contract_address(contract_name: str) -> str:
        for contract in coston2_contracts:
            if contract.get("name") == contract_name:
                return contract.get("address")
        raise ValueError(f"Contract {contract_name} not found")

    def test(self):
        address = self.get_contract_address(asset_manager_name)
        abi = asset_manager_abi
        contract = self.web3.eth.contract(address, abi=abi)
        agent_info = contract.functions.getAgentInfo(my_agent_vault).call()
        print(agent_info)

cc = ContractClient()  
cc.test()

