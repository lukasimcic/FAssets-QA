from decimal import Decimal
from typing import TYPE_CHECKING
from web3 import Web3
from src.interfaces.contracts.oft_upgradeable import OFTUpgradeable
from src.interfaces.network.networks.external_networks.external_network import ExternalNetwork
from src.utils.data_structures import UserCredentials
if TYPE_CHECKING:
    from src.interfaces.network.tokens import TokenExternalFAsset, TokenExternalNative

class HyperEVM_testnet(ExternalNetwork):
    def __init__(self, address: str):
        super().__init__()
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url()))
        self.address = address

    def get_balance(self, token: "TokenExternalNative | TokenExternalFAsset") -> Decimal:
        if token.network != type(self):
            raise ValueError(f"Token {token.name} does not belong to network {type(self).__name__}.") 
        from src.interfaces.network.tokens import TokenExternalNative, TokenExternalFAsset
        if isinstance(token, TokenExternalNative):
            balance_uba = self.web3.eth.get_balance(self.address)
            return self.web3.from_wei(balance_uba, 'ether')
        elif isinstance(token, TokenExternalFAsset):
            return OFTUpgradeable(
                network=token.network,
                token_fasset=token.token_fasset,
                sender_credentials=UserCredentials(address=self.address)
            ).get_balance()