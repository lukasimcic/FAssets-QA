from src.interfaces.contract_clients import *
from src.utils.config import token_native, token_underlying, lot_size
import random
import time

class Scenario1:
    def __init__(self, flow):
        self.flow = flow

    def run(self):
        # choose pool
        pools = self.flow.executor.get_pools()
        pool = random.choice(pools)
        pool_address = pool["Pool address"]

        # get agent vault address
        cp = CollateralPool(pool_address)
        agent_address = cp.agentVault()

        # enter pool
        balances = self.flow.executor.get_balances(log_steps=True)
        amount = random.uniform(0, balances[token_native]) 
        self.flow.executor.enter_pool(pool_address, amount, log_steps=True)

        # mint and redeem
        lot_amount = random.randint(1, balances[token_underlying] // lot_size + 1)
        self.flow.executor.mint(lot_amount, agent=agent_address, log_steps=True)
        self.flow.executor.redeem(lot_amount, log_steps=True)

        # wait timelock
        collateral_pool_token_timelock = AssetManager().collateralPoolTokenTimelockSeconds()
        time.sleep(collateral_pool_token_timelock + 1)

        # exit pool and withdraw fees
        self.flow.executor.exit_pool(pool_address, amount, log_steps=True)
        if self.flow.fc.can_withdraw_pool_fees():
            self.flow.executor.withdraw_pool_fees(pool_address, log_steps=True)

    def can(self):
        return self.flow.fc.can_enter_pool() and self.flow.fc.can_mint()