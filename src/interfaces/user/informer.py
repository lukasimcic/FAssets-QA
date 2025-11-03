from src.interfaces.network.native_networks.native_network import NativeNetwork
from src.interfaces.network.underlying_networks.underlying_network import UnderlyingNetwork
from src.interfaces.user.user import User
from src.interfaces.contracts import *


class Informer(User):
    def __init__(self, token_underlying, num=0, partner=False, config=None):
        super().__init__(token_underlying, num, partner)

    def get_balances(self, log_steps=False):
        nn = NativeNetwork( 
            self.token_native,
            self.native_data
        )
        un = UnderlyingNetwork(
            self.token_underlying,
            self.underlying_data
        )
        f = FAsset(
            self.native_data["address"],
            self.native_data["private_key"],
            self.token_underlying)
        balances = {
            self.token_native: float(nn.get_balance()),
            self.token_underlying: float(un.get_balance()),
            self.token_fasset: float(f.get_balance())
        }
        return balances
    