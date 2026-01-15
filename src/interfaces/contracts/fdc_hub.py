from typing import Optional
import toml
from src.utils.data_structures import TokenNative, UserNativeData
from src.flow.fee_tracker import FeeTracker
from .contract_client import ContractClient
from src.utils.contracts import get_contract_address

config = toml.load("config.toml")
fdc_hub_name = config["contract"]["name"]["fdc_hub"]
fdc_hub_path = config["contract"]["abi_path"]["fdc_hub"]


class FdcHub(ContractClient):
    def __init__(
            self, 
            token_native: TokenNative,
            sender_data: Optional[UserNativeData]  = None,
            fee_tracker: Optional[FeeTracker]  = None
        ):
        fdc_hub_address =  get_contract_address(fdc_hub_name, token_native)
        super().__init__(token_native, fdc_hub_path, fdc_hub_address, sender_data, fee_tracker)

    def request_attestation(self, abi_encoded: bytes, required_fee: int) -> int:
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
