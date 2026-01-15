from typing import Optional
import toml
from src.utils.data_structures import TokenNative, UserNativeData
from src.flow.fee_tracker import FeeTracker
from .contract_client import ContractClient
from src.utils.contracts import get_contract_address

config = toml.load("config.toml")
fdc_request_fee_configurations_name = config["contract"]["name"]["fdc_request_fee_configurations"]
fdc_request_fee_configurations_path = config["contract"]["abi_path"]["fdc_request_fee_configurations"]


class FdcRequestFeeConfigurations(ContractClient):
    def __init__(
            self, 
            token_native: TokenNative,
            sender_data: Optional[UserNativeData]  = None,
            fee_tracker: Optional[FeeTracker]  = None
        ):
        address = get_contract_address(fdc_request_fee_configurations_name, token_native)
        super().__init__(token_native, fdc_request_fee_configurations_path, address, sender_data, fee_tracker)

    def get_request_fee(self, data: bytes) -> int:
        required_fee = self.read(
            "getRequestFee",
            inputs=[data]
        )
        return required_fee
