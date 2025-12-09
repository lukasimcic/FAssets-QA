from src.interfaces.contracts import *
from config.config_qa import rpc_url
from src.interfaces.network.underlying_networks.underlying_network import UnderlyingBaseNetwork

from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment, Memo
from xrpl.utils import xrp_to_drops, drops_to_xrp
from xrpl.models.requests import AccountInfo, ServerInfo, Tx
from xrpl.transaction import sign, autofill, submit


class TestXRP(UnderlyingBaseNetwork):
    def __init__(self, public_key, private_key, fee_tracker):
        super().__init__(fee_tracker=fee_tracker)
        self.client = JsonRpcClient(rpc_url["testXRP"])
        if public_key and private_key: # otherwise this class is used for address non specific operations
            self.wallet = Wallet(public_key, private_key)
        self.asset_unit_uba = AssetManager("testXRP").asset_unit_uba()

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
        # full balance
        acct_info = AccountInfo(
            account=self.wallet.classic_address, 
            ledger_index="validated", 
            strict=True
            )
        response = self.client.request(acct_info)
        balance_drops = response.result["account_data"]["Balance"]
        balance = float(drops_to_xrp(balance_drops))
        # reserved balance
        owner_count = response.result["account_data"].get("OwnerCount", 0)
        server_info = self.client.request(ServerInfo())
        validated_ledger = server_info.result["info"]["validated_ledger"]
        reserve_base = validated_ledger["reserve_base_xrp"]
        reserve_inc = validated_ledger["reserve_inc_xrp"]
        reserved_balance = reserve_base + (owner_count * reserve_inc)
        # available balance
        available_balance = balance - reserved_balance
        return available_balance
    
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
        self.fee_tracker.underlying_gas_fees += float(drops_to_xrp(response.result["tx_json"]["Fee"]))
        return {
            "tx_hash": response.result["tx_json"]["hash"],
            "amount": amount
        }
    
    def get_current_block(self):
        response = self.client.request(ServerInfo())
        return int(response.result["info"]["validated_ledger"]["seq"])
    
    def get_block_of_tx(self, tx_hash):
        """
        Returns the block number of the given transaction hash.
        """
        response = self.client.request(Tx(transaction=tx_hash))
        return int(response.result["ledger_index"])
