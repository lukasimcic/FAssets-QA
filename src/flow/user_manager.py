import json
import os
from pathlib import Path
from typing import Optional, TYPE_CHECKING
import toml
from src.actions.core_actions.core_actions import core_actions
from src.interfaces.user.state_manager import StateManager
from src.utils.data_structures import UserData
from src.interfaces.network.tokens import TokenNative, TokenUnderlying
from src.utils.secrets import get_user_nums
from src.interfaces.user.funder import Funder
from src.utils.data_storage import remove_inactive_records_for_user
if TYPE_CHECKING:
    from src.interfaces.network.networks.native_networks.native_network import NativeNetwork
    from src.interfaces.network.networks.underlying_networks.underlying_network import UnderlyingNetwork

config = toml.load("config.toml")
secrets_folder = Path(config["folder"]["secrets"])

ENCRYPTION_PASSWORD : str = os.environ["ENCRYPTION_PASSWORD"]
INDEXER : str = os.environ["INDEXER"]
API_KEYS : dict["NativeNetwork | UnderlyingNetwork", str] = {
    TokenNative.C2FLR.network: os.environ["COSTON2_API_KEY"],
    TokenUnderlying.testXRP.network: os.environ["XRPL_TESTNET_API_KEY"]
}

# TODO: unify naming in secrets, check usage in fasset-bots
class UserManager():
    def __init__(self, token_native: "TokenNative", token_underlying: "TokenUnderlying", user_nums: Optional[list[int]]  = None):
        self.token_native = token_native
        self.token_underlying = token_underlying
        self.wallet_data = {
            "encryption_password": ENCRYPTION_PASSWORD,
        }
        self.api_key_data = {
            "indexer": [INDEXER],
            "xrp_rpc": API_KEYS[self.token_underlying.network],
            "native_rpc": API_KEYS[self.token_native.network],
        }
        self.user_nums = user_nums
        if self.funder_exists():
            self.funder = Funder(self.token_native, self.token_underlying, user_nums)

    def _generate_credentials(
            self, 
            secrets_underlying: Optional[dict[str, str]], 
            secrets_native: Optional[dict[str, str]]
            ) -> dict[str, dict[str, str]]:
        if not secrets_underlying:
            un = self.token_underlying.network()
            secrets_underlying = un.generate_new_address()
        if not secrets_native:
            nn = self.token_native.network()
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
    
    def generate(
            self, 
            funder=False, 
            secrets_underlying: Optional[dict[str, str]] = None, 
            secrets_native: Optional[dict[str, str]] = None
            ) -> None:
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
            if "partner" in file:
                credentials = self._generate_credentials(None, None)
            else:
                credentials = self._generate_credentials(secrets_underlying, secrets_native)
            secrets = {
                "wallet": self.wallet_data,
                "apiKey": self.api_key_data,
                "user": credentials
            }
            with open(folder / file, "w") as f:
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

    def remove_inactive_records(self, cli : bool = False) -> None:
        for user_num in self.user_nums:
            user_data = UserData(
                token_native=self.token_native,
                token_underlying=self.token_underlying,
                num=user_num
            )
            ca = core_actions(user_data, cli)
            remove_inactive_records_for_user(user_data, ca)

