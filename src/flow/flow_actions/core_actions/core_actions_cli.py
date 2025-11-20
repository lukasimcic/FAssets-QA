from src.interfaces.user.user_bot import UserBot
from src.flow.flow_actions.core_actions.core_actions import CoreActions

class CoreActionsCli(CoreActions):
    def __init__(self, executor : UserBot):
        super().__init__()
        self.executor = executor

    # core actions

    def mint(self, lot_amount, agent=None, log_steps=False):
        self.executor.mint(lot_amount, agent=agent, log_steps=log_steps)

    def redeem(self, lot_amount, log_steps=False):
        self.executor.redeem(lot_amount, log_steps=log_steps)

    def enter_pool(self, pool_address, amount, log_steps=False):
        self.executor.enter_pool(pool_address, amount, log_steps=log_steps)

    def exit_pool(self, pool_address, amount, log_steps=False):
        self.executor.exit_pool(pool_address, amount, log_steps=log_steps)

    def get_agents(self, log_steps=False):
        return self.executor.get_agents(log_steps=log_steps)

    def withdraw_pool_fees(self, pool_address, log_steps=False):
        self.executor.withdraw_pool_fees(pool_address, log_steps=log_steps)

    def mint_execute(self, mint_id, log_steps=False):
        self.executor.execute_mint(mint_id, log_steps=log_steps)

    def redeem_default(self, redemption_id, log_steps=False):
        self.executor.redeem_default(redemption_id, log_steps=log_steps)