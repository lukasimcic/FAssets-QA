from decimal import Decimal

from src.interfaces.user.user_bot import UserBot
from src.actions.core_actions.core_actions import CoreActions
from src.utils.data_structures import Balances, MintStatus, RedemptionStatus, Pool, UserData, PoolHolding, AgentInfo


class CoreActionsCLI(CoreActions):
    def __init__(self, user_data : UserData):
        super().__init__()
        self.user_bot = UserBot(user_data)

    # state retrieval

    def get_balances(self, log_steps: bool = False) -> Balances:
        return self.user_bot.get_balances(log_steps=log_steps)

    def get_pools(self, log_steps: bool = False) -> list[Pool]:
        return self.user_bot.get_pools(log_steps=log_steps)

    def get_pool_holdings(self, log_steps: bool = False) -> list[PoolHolding]:
        return self.user_bot.get_pool_holdings(log_steps=log_steps)

    def get_mint_status(self, log_steps: bool = False) -> MintStatus:
        return self.user_bot.get_mint_status(log_steps=log_steps)
    
    def get_redemption_status(self, log_steps: bool = False) -> RedemptionStatus:
        return self.user_bot.get_redemption_status(log_steps=log_steps)
    
    # logging
    
    def log(self, message: str) -> None:
        self.user_bot.log_step(message, True)

    # actions implementation

    def mint(self, lot_amount: int, agent: str = None, log_steps: bool = False) -> None:
        self.user_bot.mint(lot_amount, agent=agent, log_steps=log_steps)

    def redeem(self, lot_amount: int, log_steps: bool = False) -> None:
        self.user_bot.redeem(lot_amount, log_steps=log_steps)

    def enter_pool(self, pool_address: str, amount: Decimal, log_steps: bool = False) -> None:
        self.user_bot.enter_pool(pool_address, amount, log_steps=log_steps)

    def exit_pool(self, pool_address: str, amount: Decimal, log_steps: bool = False) -> None:
        self.user_bot.exit_pool(pool_address, amount, log_steps=log_steps)

    def get_agents(self, log_steps: bool = False) -> list[AgentInfo]:
        return self.user_bot.get_agents(log_steps=log_steps)

    def withdraw_pool_fees(self, pool_address: str, fees: Decimal, log_steps: bool = False) -> None:
        self.user_bot.withdraw_pool_fees(pool_address, fees, log_steps=log_steps)

    def mint_execute(self, mint_id: int, log_steps: bool = False) -> None:
        self.user_bot.execute_mint(mint_id, log_steps=log_steps)

    def redeem_default(self, redemption_id: int, log_steps: bool = False) -> None:
        self.user_bot.redeem_default(redemption_id, log_steps=log_steps)

    # not implemented

    def transfer_pool_tokens(self, pool_address: str, to_address: str, amount: Decimal, log_steps: bool = False) -> None:
        raise NotImplementedError("transfer_pool_tokens is not implemented in CLI mode.")