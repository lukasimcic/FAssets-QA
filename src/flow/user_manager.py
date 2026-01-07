import os
from src.interfaces.user.state_manager import StateManager
from src.utils.data_structures import TokenNative, TokenUnderlying, UserData
from src.utils.secrets import get_user_nums
from src.interfaces.network.native_networks.native_network import NativeNetwork
from src.interfaces.network.underlying_networks.underlying_network import UnderlyingNetwork
from src.interfaces.user.funder import Funder
from config.config_qa import secrets_folder


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
        self.user_nums = user_nums
        if self.funder_exists():
            self.funder = Funder(self.token_native, self.token_underlying, user_nums)

    def _generate_credentials(self) -> dict[str, dict[str, str]]:
        un = UnderlyingNetwork(self.token_underlying)
        secrets_underlying = un.generate_new_address()
        nn = NativeNetwork(self.token_native)
        secrets_native = nn.generate_new_address()
        return {
            "native": secrets_native,  
            self.token_underlying.name: secrets_underlying
        }
    
    def _get_next_user_num(self) -> int:
        if self.user_nums is None:
            user_nums = get_user_nums()
        else:
            user_nums = self.user_nums
        return max(user_nums + [-1]) + 1
    
    def generate(self, funder=False) -> None:
        if funder:
            folders = [secrets_folder]
            files = ["funder.json"]
        else:
            user_num = self._get_next_user_num()
            folders = []
            files = []
            for user in ["user", "user_partner"]:
                folders.append(secrets_folder / user)
                files.append(f"{user}_{user_num}.json")
        for folder, file in zip(folders, files):
            if not folder.exists():
                os.makedirs(folder)
            credentials = self._generate_credentials()
            secrets = {
                "wallet": self.wallet_data,
                "apiKey": self.api_key_data,
                "user": credentials
            }
            with open(folder / file, "w") as f:
                import json
                json.dump(secrets, f, indent=4)

    def funder_exists(self) -> bool:
        return os.path.exists(secrets_folder / "funder.json")

    def request_funds(self) -> None:
        self.funder.request_funds()

    def distribute_funds(self) -> None:
        self.funder.distribute_funds()

    def collect_funds(self) -> None:
        self.funder.collect_funds()

    def print_funder_balances(self) -> None:
        sm = StateManager(
            UserData(
                token_native=self.token_native,
                token_underlying=self.token_underlying,
                funder=True
            )
        )
        balances = sm.get_balances()
        print(f"Funder balances: {balances}")

    

