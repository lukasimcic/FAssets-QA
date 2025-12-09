from src.utils.data_structures import TokenUnderlying, UserNativeData
from src.utils.fee_tracker import FeeTracker
from .contract_client import ContractClient
from src.interfaces.contracts.asset_manager import AssetManager
from src.utils.contracts import get_contract_address
from config.config_qa import fasset_path, fasset_testxrp_instance_name


class FAsset(ContractClient):
    def __init__(
            self, 
            token_underlying: TokenUnderlying, 
            sender_data: UserNativeData | None = None,
            fee_tracker: FeeTracker | None = None
        ):
        self.token_underlying = token_underlying
        match token_underlying:
            case "testXRP": 
                fasset_instance_name = fasset_testxrp_instance_name
            case _:
                raise ValueError(f"Unsupported underlying token: {token_underlying}")
        fasset_address =  get_contract_address(fasset_instance_name)
        super().__init__(fasset_path, fasset_address, sender_data, fee_tracker)

    def get_balance(self):
        return self.balance_of(self.sender_address)

    def balance_of(self, address):
        am = AssetManager(self.token_underlying, self.sender_data)
        am.asset_unit_uba()
        balance_uba = self.read("balanceOf", inputs=[address])
        return balance_uba / am.asset_unit_uba()