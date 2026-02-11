from typing import Optional
from src.interfaces.network.tokens import Token, TokenNative, TokenUnderlying, TokenFAsset, TokenExternalNative, TokenExternalFAsset
from src.interfaces.contracts.oft_upgradeable import OFTUpgradeable
from src.flow.fee_tracker import FeeTracker
from src.interfaces.user.user import User
from src.interfaces.contracts import *
from src.utils.data_structures import Balances, UserData


class StateManager(User):
    def __init__(self, user_data : UserData, fee_tracker : Optional[FeeTracker]  = None):
        super().__init__(user_data, fee_tracker)

    def get_balances(self, tokens: Optional[list[Token]] = None, log_steps: bool = False) -> Balances:
        if not tokens:
            tokens = [self.token_native, self.token_underlying, self.token_fasset]
        balances_dict = {}
        for token in tokens:
            if isinstance(token, TokenNative):
                nn = self.token_native.network(self.native_credentials)
                balances_dict[token] = nn.get_balance()
            elif isinstance(token, TokenUnderlying):
                un = self.token_underlying.network(self.underlying_credentials)
                balances_dict[token] = un.get_balance()
            elif isinstance(token, TokenFAsset):
                f = FAsset(
                    self.native_network,
                    self.token_fasset,
                    self.native_credentials
                )
                balances_dict[token] = f.get_balance()
            elif isinstance(token, TokenExternalNative):
                # TODO: implement external native balance retrieval
                for token_fasset in tokens:
                    if isinstance(token_fasset, TokenFAsset):
                        token = TokenExternalFAsset.from_underlying(token_fasset.token_underlying, token)
                        balances_dict[token] = OFTUpgradeable(
                            token_fasset,
                            self.native_credentials
                        ).get_balance()
        balances = Balances(data=balances_dict)
        return balances
    
    def block_underlying_deposits(self) -> None:
        un = self.token_underlying.network(self.underlying_credentials)
        un.block_all_deposits()

    def unblock_underlying_deposits(self) -> None:
        un = self.token_underlying.network(self.underlying_credentials)
        un.unblock_all_deposits()
    