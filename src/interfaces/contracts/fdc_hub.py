from src.utils.data_structures import TokenNative, UserNativeData
from src.flow.fee_tracker import FeeTracker
from .contract_client import ContractClient
from src.utils.contracts import get_contract_address
from config.config_qa import fdc_hub_path, fdc_hub_instance_name

class FdcHub(ContractClient):
    def __init__(
            self, 
            token_native: TokenNative,
            sender_data: UserNativeData | None = None,
            fee_tracker: FeeTracker | None = None
        ):
        fdc_hub_address =  get_contract_address(fdc_hub_instance_name)
        super().__init__(token_native, fdc_hub_path, fdc_hub_address, sender_data, fee_tracker)

    def request_attestation(self, abi_encoded, required_fee):
        """
        Request attestation from FDC Hub contract.
        Returns the block number of the transaction.
        """
        receipt = self.write(
            "requestAttestation",
            inputs=[abi_encoded],
            value=required_fee
        )["receipt"]
        return int(receipt.blockNumber)
