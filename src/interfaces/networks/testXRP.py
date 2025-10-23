from src.interfaces.contracts import *
from src.utils.config import rpc_url_xrp
from src.interfaces.networks.network import BaseNetwork

from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment, Memo
from xrpl.utils import xrp_to_drops, drops_to_xrp
from xrpl.models.requests import AccountInfo, ServerInfo
from xrpl.transaction import sign, autofill, submit


class TestXRP(BaseNetwork):
    def __init__(self, public_key, private_key):
        super().__init__()
        self.client = JsonRpcClient(rpc_url_xrp)
        self.wallet = Wallet(public_key, private_key)
        self.asset_unit_uba = AssetManager("", "", "testXRP").asset_unit_uba()

    @staticmethod
    def generate_address():
        wallet = Wallet.create()
        secrets = {
            "public_key": wallet.public_key,
            "private_key": wallet.private_key,
            "address": wallet.classic_address
            }
        return secrets

    def get_balance(self):
        acct_info = AccountInfo(
            account=self.wallet.classic_address, 
            ledger_index="validated", 
            strict=True
            )
        response = self.client.request(acct_info)
        balance_drops = response.result["account_data"]["Balance"]
        return drops_to_xrp(balance_drops)
    
    def send_transaction(self, to_address, amount, memo_data=None):
        payment = Payment(
            account=self.wallet.classic_address,
            amount=xrp_to_drops(amount),
            destination=to_address,
            memos=[Memo(memo_data=memo_data)] if memo_data else None
        )
        autofilled_tx = autofill(payment, self.client)
        signed_tx = sign(autofilled_tx, self.wallet)
        response = submit(signed_tx, self.client)
        return response
