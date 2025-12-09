from src.actions.action_bundle import ActionBundle
from src.actions.helper_functions import can_mint, can_enter_pool
from src.interfaces.contracts import *
import random
import time
    
    
class Scenario1(ActionBundle):
    def __init__(self, user_data, flow_state, cli):
        super().__init__(user_data, flow_state, cli)


    def action(self):
        # choose pool
        pool = random.choice(self.pools)
        pool_address = pool.address

        # get agent vault address
        cp = CollateralPool(pool_address)
        agent_address = cp.agent_vault()

        # enter pool
        amount = random.uniform(0, self.balances[self.token_native])
        self.ca.enter_pool(pool_address, amount, log_steps=True)

        # mint and redeem
        lot_amount = random.randint(1, self.balances[self.token_underlying] // self.lot_size + 1)
        self.ca.mint(lot_amount, agent=agent_address, log_steps=True)
        self.ca.redeem(lot_amount, log_steps=True)

        # wait timelock
        am = AssetManager(self.token_underlying)
        collateral_pool_token_timelock = am.collateral_pool_token_timelock_seconds()
        time.sleep(collateral_pool_token_timelock + 1)

        # exit pool and withdraw fees
        self.ca.exit_pool(pool_address, amount, log_steps=True)
        self.ca.withdraw_pool_fees(pool_address, log_steps=True)


    def condition(self):
        enter_pool_condition = can_enter_pool(self.balances, self.token_underlying)
        mint_condition = can_mint(self.balances, self.token_underlying, self.lot_size, self.ca.get_agents())
        return enter_pool_condition and mint_condition

    def state_after(self):
        raise NotImplementedError("State update is not implemented yet.")