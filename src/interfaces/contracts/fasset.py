from .contract_client import ContractClient
from src.interfaces.contracts.asset_manager import AssetManager
from src.utils.contracts import get_contract_address
from src.utils.config import fasset_path, fasset_testxrp_instance_name


class FAsset(ContractClient):
    def __init__(self, sender_address, sender_private_key, token_underlying):
        self.token_underlying = token_underlying
        match token_underlying:
            case "testXRP": 
                fasset_instance_name = fasset_testxrp_instance_name
            case _:
                raise ValueError(f"Unsupported underlying token: {token_underlying}")
        fasset_address =  get_contract_address(fasset_instance_name)
        super().__init__(sender_address, sender_private_key, fasset_path, fasset_address)

    def get_balance(self):
        return self.balance_of(self.sender_address)

    def balance_of(self, address):
        am = AssetManager(self.sender_address, self.sender_private_key, self.token_underlying)
        am.asset_unit_uba()
        balance_uba = self.read("balanceOf", inputs=[address])
        return balance_uba / am.asset_unit_uba()