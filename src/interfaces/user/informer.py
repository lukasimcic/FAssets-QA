from src.interfaces.network.native_networks.native_network import NativeNetwork
from src.interfaces.network.underlying_networks.underlying_network import UnderlyingNetwork
from src.interfaces.user.user import User
from src.interfaces.contracts import *
from src.utils.data_structures import Balances, UserData


class Informer(User):
    def __init__(self, user_data : UserData):
        super().__init__(user_data)

    def get_balances(self, log_steps: bool = False) -> Balances:
        nn = NativeNetwork( 
            self.token_native,
            self.native_data
        )
        un = UnderlyingNetwork(
            self.token_underlying,
            self.underlying_data
        )
        f = FAsset(
            self.token_native,
            self.token_underlying,
            self.native_data
        )
        balances = Balances(data={
            self.token_native: nn.get_balance(),
            self.token_underlying: un.get_balance(),
            self.token_fasset: f.get_balance()
        })
        return balances
    