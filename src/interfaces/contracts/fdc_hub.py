from .contract_client import ContractClient
from src.utils.contracts import get_contract_address
from src.utils.config import fdc_hub_path, fdc_hub_instance_name

class FdcHub(ContractClient):
    def __init__(self, sender_address, sender_private_key):
        fdc_hub_address =  get_contract_address(fdc_hub_instance_name)
        super().__init__(sender_address, sender_private_key, fdc_hub_path, fdc_hub_address)

    def request_attestation(self, abi_encoded, required_fee):
        """
        Request attestation from FDC Hub contract.
        Returns the block number of the transaction.
        """
        _, receipt = self.write(
            "requestAttestation",
            inputs=[abi_encoded],
            value=required_fee,
            return_receipt=True
        )
        return int(receipt.blockNumber)
