from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from src.interfaces.network.networks.external_networks.external_network import ExternalNetwork
if TYPE_CHECKING:
    from src.utils.data_structures import UserCredentials


class HyperEVM_testnet(ExternalNetwork):
    def __init__(self, credentials: Optional["UserCredentials"] = None):
        super().__init__()

    def get_balance(self) -> Decimal:
        pass # TODO