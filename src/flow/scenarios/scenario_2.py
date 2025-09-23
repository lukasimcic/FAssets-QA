from src.interfaces.contract_clients import *
from src.utils.config import *
import random
import time

class Scenario2:
    def __init__(self, flow):
        self.flow = flow

    def run(self):
        # choose pool
        pools = self.flow.executor.get_pools()
        pool = random.choice(pools)
        pool_address = pool["Pool address"]

        # enter pool
        balances = self.flow.executor.get_balances(log_steps=True)
        amount = random.uniform(0, balances[token_native]) 
        self.flow.executor.enter_pool(pool_address, amount, log_steps=True)

        # wait timelock
        collateral_pool_token_timelock = AssetManager().collateralPoolTokenTimelockSeconds()
        time.sleep(collateral_pool_token_timelock + 1)

        # get the amount of debt-free pool tokens 
        print(pool_address)
        cp = CollateralPool(pool_address)
        print(self.flow.executor.native_address)
        debt_free_tokens = cp.debtFreeTokensOf(self.flow.executor.native_address)
        if debt_free_tokens == 0:
            self.flow.executor.logger.info("No debt-free pool tokens available")
        else:
            self.flow.executor.logger.info(f"Debt free pool tokens: {debt_free_tokens}")
            amount = min(int(amount * 10 ** decimals), debt_free_tokens)

            # transfer pool tokens to partner bot
            pool_token_address = cp.poolToken()
            pt = CollateralPoolToken(pool_token_address)
            print(amount, type(amount))
            print(self.flow.partner_executor.native_address)
            pt.transfer(
                self.flow.executor.native_address,
                self.flow.executor.native_private_key,
                self.flow.partner_executor.native_address,
                amount
            )
            self.flow.executor.logger.info(f"Transferred {amount} of pool tokens to partner bot.")
            self.flow.partner_executor.logger.info(f"Got {amount} of pool tokens from user bot.")

            # exit pool from partner bot
            time.sleep(5)
            self.flow.partner_executor.exit_pool(pool_address, log_steps=True)

    def can(self):
        return self.flow.fc.can_enter_pool()