from src.utils.config import rpc_url
from src.utils.contracts import get_contract_abi
from web3 import Web3
from web3.middleware import geth_poa_middleware


class ContractClient:
    def __init__(self, contract_path: str, contract_address: str, timeout: int | None = None):
        self.path = contract_path
        self.name = contract_address
        
        kwargs = {}
        if timeout is not None:
            kwargs['timeout'] = timeout
        self.web3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs=kwargs))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        assert self.web3.is_connected()
        contract_abi = get_contract_abi(contract_path)
        self.contract = self.web3.eth.contract(contract_address, abi=contract_abi)

