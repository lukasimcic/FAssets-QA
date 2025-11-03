from .contract_client import ContractClient
from src.utils.contracts import get_contract_address
from config.config_qa import fdc_request_fee_configurations_path, fdc_request_fee_configurations_instance_name

class FdcRequestFeeConfigurations(ContractClient):
    def __init__(self, sender_address, sender_private_key):
        address =  get_contract_address(fdc_request_fee_configurations_instance_name)
        super().__init__(sender_address, sender_private_key, fdc_request_fee_configurations_path, address)

    def get_request_fee(self, data):
        required_fee = self.read(
            "getRequestFee",
            inputs=[data]
        )
        return required_fee
