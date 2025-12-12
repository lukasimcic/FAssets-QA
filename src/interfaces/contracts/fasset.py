from src.utils.data_structures import TokenFasset, TokenNative, TokenUnderlying, UserNativeData
from src.utils.fee_tracker import FeeTracker
from .contract_client import ContractClient
from src.interfaces.contracts.asset_manager import AssetManager
from src.utils.contracts import get_contract_address
from config.config_qa import fasset_path


class FAsset(ContractClient):
    def __init__(
            self, 
            token_native: TokenNative,
            token_underlying: TokenUnderlying, 
            sender_data: UserNativeData | None = None,
            fee_tracker: FeeTracker | None = None
        ):
        self.token_underlying = token_underlying
        fasset_address =  get_contract_address(token_underlying.fasset_instance_name)
        super().__init__(token_native, fasset_path, fasset_address, sender_data, fee_tracker)

    def get_balance(self):
        return self.balance_of(self.sender_address)

    def balance_of(self, address):
        balance_uba = self.read("balanceOf", inputs=[address])
        token_fasset = TokenFasset.from_underlying(self.token_underlying)
        return token_fasset.from_uba(balance_uba)