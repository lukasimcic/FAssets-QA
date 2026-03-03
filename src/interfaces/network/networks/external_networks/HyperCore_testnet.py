from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from hyperliquid.info import Info
from hyperliquid.utils import constants
from src.interfaces.network.networks.external_networks.external_network import ExternalNetwork
if TYPE_CHECKING:
    from src.interfaces.network.tokens import TokenExternalFAsset, TokenExternalNative


class HyperCore_testnet(ExternalNetwork):
    evm = False
    def __init__(self, address: Optional[str] = None):
        super().__init__()
        self.address = address

    def get_balance(self, token: "TokenExternalNative | TokenExternalFAsset") -> Decimal:
        if token.network != type(self):
            raise ValueError(f"Token {token.name} does not belong to network {type(self).__name__}.") 
        token_name = token.name.split("_")[0].replace("Test", "")
        info = Info(constants.TESTNET_API_URL, skip_ws=True)
        spot_user_state = info.spot_user_state(self.address)
        for token_state in spot_user_state["balances"]:
            if token_state["coin"] == token_name:
                return Decimal(token_state["total"])
        return Decimal(0)