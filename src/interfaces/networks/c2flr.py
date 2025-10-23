from src.interfaces.networks.network import BaseNetwork
from src.utils.config import rpc_url_c2flr 
from web3 import Web3

class C2FLR(BaseNetwork):
    def __init__(self, address, private_key):
        super().__init__()
        self.web3 = Web3(Web3.HTTPProvider(rpc_url_c2flr))
        self.address = address
        self.private_key = private_key

    def get_balance(self):
        balance_wei = self.web3.eth.get_balance(self.address)
        balance = self.web3.from_wei(balance_wei, 'ether')
        return balance
    
    def send_transaction(self, to_address, amount):
        # implement as needed
        raise NotImplementedError("C2FLR send_transaction not implemented yet.")