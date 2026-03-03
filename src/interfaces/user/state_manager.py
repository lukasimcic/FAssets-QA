from typing import TYPE_CHECKING, Optional
from src.interfaces.network.tokens import TokenNative, TokenUnderlying, TokenFAsset, TokenExternalNative, TokenExternalFAsset
from src.interfaces.contracts.oft_upgradeable import OFTUpgradeable
from src.interfaces.user.user import User
from src.interfaces.contracts import *
from src.utils.data_structures import Balances
if TYPE_CHECKING:
    from src.utils.data_structures import UserData
    from src.flow.fee_tracker import FeeTracker
    from src.interfaces.network.tokens import Token


class StateManager(User):
    def __init__(self, user_data : "UserData", fee_tracker : Optional["FeeTracker"]  = None):
        super().__init__(user_data, fee_tracker)

    def get_balances(self, tokens: Optional[list["Token"]] = None, log_steps: bool = False) -> "Balances":
        if not tokens:
            tokens = [self.token_native, self.token_underlying, self.token_fasset]
        balances_dict = {}
        for token in tokens:
            if isinstance(token, (TokenNative, TokenFAsset)):
                nn = self.token_native.network(self.native_credentials)
                balances_dict[token] = nn.get_balance(token)
            elif isinstance(token, TokenUnderlying):
                un = self.token_underlying.network(self.underlying_credentials)
                balances_dict[token] = un.get_balance(token)
            elif isinstance(token, (TokenExternalNative, TokenExternalFAsset)):
                en = token.network(self.native_credentials.address)
                balances_dict[token] = en.get_balance(token)
        balances = Balances(data=balances_dict)
        return balances
    
    def block_underlying_deposits(self) -> None:
        un = self.token_underlying.network(self.underlying_credentials)
        un.block_all_deposits()

    def unblock_underlying_deposits(self) -> None:
        un = self.token_underlying.network(self.underlying_credentials)
        un.unblock_all_deposits()
    