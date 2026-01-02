from src.interfaces.user.informer import Informer
from src.utils.data_structures import TokenNative, TokenUnderlying, UserData
from src.utils.secrets import get_user_nums
from src.interfaces.network.native_networks.native_network import NativeNetwork
from src.interfaces.network.underlying_networks.underlying_network import UnderlyingNetwork
from src.interfaces.user.funder import Funder
from config.config_qa import secrets_folder
import os, re

# TODO: unify naming in secrets, check usage in fasset-bots
class UserManager():
    def __init__(self, token_native: TokenNative, token_underlying: TokenUnderlying, user_nums: list[int] | None = None):
        self.token_native = token_native
        self.token_underlying = token_underlying
        self.wallet_data = {
            "encryption_password": "muilebA0!muilebA0!"
        }
        self.api_key_data = {
            "indexer": ["123456"],
            "xrp_rpc": "4tg3AxysaZodxTqsCtcMnBdBIEkR6KDKGTdqBEA8g9MKq4bH",
            "native_rpc": "96526d46-91d8-4a1b-8ea7-80b2179ea840",
        }
        if user_nums is None:
            self.user_nums = get_user_nums()
        else:
            self.user_nums = user_nums
        self.funder = Funder(self.token_native, self.token_underlying)

    def _generate_credentials(self):
        un = UnderlyingNetwork(self.token_underlying)
        secrets_underlying = un.generate_new_address()
        nn = NativeNetwork(self.token_native)
        secrets_native = nn.generate_new_address()
        return {
            "native": secrets_native,  
            self.token_underlying.name: secrets_underlying
        }
    
    def _get_next_user_num(self):
        return max(self.user_nums + [0]) + 1
    
    def generate(self):
        user_num = self._get_next_user_num()
        for user in ["user", "user_partner"]:
            folder = secrets_folder / user
            if not folder.exists():
                os.makedirs(folder)
            credentials = self._generate_credentials()
            secrets = {
                "wallet": self.wallet_data,
                "apiKey": self.api_key_data,
                "user": credentials
            }
            with open(folder / f"{user}_{user_num}.json", "w") as f:
                import json
                json.dump(secrets, f, indent=4)

    def request_funds(self):
        self.funder.request_funds()

    def distribute_funds(self):
        self.funder.distribute_funds()

    def collect_funds(self):
        self.funder.collect_funds()
    

