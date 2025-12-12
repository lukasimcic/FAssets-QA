from src.interfaces.network.native_networks.native_network import NativeBaseNetwork
from src.utils.data_structures import TokenNative
from web3 import Web3
from web3.middleware import geth_poa_middleware


class C2FLR(NativeBaseNetwork):
    def __init__(self, address, private_key):
        super().__init__()
        self.token_native = TokenNative.C2FLR
        self.web3 = Web3(Web3.HTTPProvider(self.token_native.rpc_url))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.address = address
        self.private_key = private_key

    def get_balance(self):
        balance_uba = self.web3.eth.get_balance(self.address)
        return self.token_native.from_uba(balance_uba)

    def _get_current_block(self):
        return self.web3.eth.block_number
    
    def get_current_timestamp(self):
        current_block = self._get_current_block()
        block = self.web3.eth.get_block(current_block)
        return block.timestamp