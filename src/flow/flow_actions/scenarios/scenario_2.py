from src.flow.flow_actions.action_bundle import ActionBundle
from src.flow.flow_actions.pool import can_enter_pool
from src.interfaces.contracts import *
import random
import time


class Scenario2(ActionBundle):
    def __init__(self, ca, ca_partner, user, partner, lot_size, state):
        super().__init__(ca, ca_partner, user, partner, lot_size, state)


    def action(self):
        # choose pool
        pool = random.choice(self.pools)
        pool_address = pool["Pool address"]

        # enter pool
        amount = random.uniform(0, self.balances[self.token_native])
        self.ca.enter_pool(pool_address, amount, log_steps=True)

        # wait timelock
        am = AssetManager("", "", self.token_underlying)
        collateral_pool_token_timelock = am.collateral_pool_token_timelock_seconds()
        time.sleep(collateral_pool_token_timelock + 1)

        # get the amount of debt-free pool tokens
        cp = CollateralPool("", "", pool_address)
        debt_free_tokens = cp.debt_free_tokens_of(self.native_address)
        if debt_free_tokens == 0:
            self.logger.info("No debt-free pool tokens available")
        else:
            self.logger.info(f"Debt free pool tokens: {debt_free_tokens}")
            amount = min(int(amount * am.asset_unit_uba()), debt_free_tokens)

            # transfer pool tokens to partner bot
            pool_token_address = cp.pool_token()
            pt = CollateralPoolToken(self.native_address, self.native_private_key, pool_token_address)
            pt.transfer(self.partner_native_address, amount)
            self.logger.info(f"Transferred {amount} of pool tokens to partner bot.")
            self.partner_logger.info(f"Got {amount} of pool tokens from user bot.")

            # exit pool from partner bot
            time.sleep(5)
            self.ca_partner.exit_pool(pool_address, log_steps=True)

    
    def condition(self):
        return can_enter_pool(self.balances, self.token_underlying)


    def state_after(self):
        raise NotImplementedError("State update is not implemented yet.")