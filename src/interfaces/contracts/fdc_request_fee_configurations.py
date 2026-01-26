from typing import Optional
from src.utils.data_structures import TokenNative, UserNativeData
from src.flow.fee_tracker import FeeTracker
from .contract_client import ContractClient
from src.utils.contracts import get_contract_names


class FdcRequestFeeConfigurations(ContractClient):
    def __init__(
            self, 
            token_native: TokenNative,
            sender_data: Optional[UserNativeData]  = None,
            fee_tracker: Optional[FeeTracker]  = None
        ):
        names = get_contract_names(self)
        super().__init__(names, token_native, sender_data=sender_data, fee_tracker=fee_tracker)

    def get_request_fee(self, data: bytes) -> int:
        required_fee = self.read(
            "getRequestFee",
            inputs=[data]
        )
        return required_fee
