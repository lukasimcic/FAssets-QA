from typing import Optional
from src.interfaces.contracts.oft_upgradeable import OFTUpgradeable
from src.flow.fee_tracker import FeeTracker
from src.interfaces.network.native_networks.native_network import NativeNetwork
from src.interfaces.network.underlying_networks.underlying_network import UnderlyingNetwork
from src.interfaces.user.user import User
from src.interfaces.contracts import *
from src.utils.data_structures import Balances, Token, TokenBridged, UserData, TokenNative, TokenUnderlying, TokenFasset


class StateManager(User):
    def __init__(self, user_data : UserData, fee_tracker : Optional[FeeTracker]  = None):
        super().__init__(user_data, fee_tracker)

    def get_balances(self, tokens: Optional[list[Token]] = None, log_steps: bool = False) -> Balances:
        if not tokens:
            tokens = [self.token_native, self.token_underlying, self.token_fasset]
        balances_dict = {}
        for token in tokens:
            if isinstance(token, TokenNative):
                nn = NativeNetwork(
                    self.token_native,
                    self.native_data
                )
                balance = nn.get_balance()
            elif isinstance(token, TokenUnderlying):
                un = UnderlyingNetwork(
                    self.token_underlying,
                    self.underlying_data
                )
                balance = un.get_balance()
            elif isinstance(token, TokenFasset):
                f = FAsset(
                    self.token_native,
                    self.token_underlying,
                    self.native_data
                )
                balance = f.get_balance()
            elif isinstance(token, TokenBridged):
                ou = OFTUpgradeable(token, self.native_data)
                balance = ou.get_balance()
            balances_dict[token] = balance
        balances = Balances(data=balances_dict)
        return balances
    
    def block_underlying_deposits(self) -> None:
        un = UnderlyingNetwork(
            self.token_underlying,
            self.underlying_data
        )
        un.block_all_deposits()

    def unblock_underlying_deposits(self) -> None:
        un = UnderlyingNetwork(
            self.token_underlying,
            self.underlying_data
        )
        un.unblock_all_deposits()
    