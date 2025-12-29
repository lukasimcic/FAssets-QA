from src.actions.action_bundle import ActionBundle
from src.actions.helper_functions import can_enter_pool, collateral_to_tokens, tokens_to_collateral
from src.interfaces.contracts import *
from src.utils.data_structures import PoolHolding
import random
import time



class Scenario2(ActionBundle):
    def __init__(self, user_data, flow_state, cli):
        super().__init__(user_data, flow_state, cli)
        self.partner_involved = True
    

    def condition(self):
        return can_enter_pool(self.balances, self.token_underlying)


    def action(self):
        # choose pool
        pool = random.choice(self.ca.get_pools())
        pool_address = pool.address

        # enter pool
        enter_amount_collateral = random.uniform(0, self.balances[self.token_native])
        enter_amount_tokens = collateral_to_tokens(self.token_native, pool_address, enter_amount_collateral)
        self.ca.enter_pool(pool_address, enter_amount_collateral, log_steps=True)

        # wait timelock
        am = AssetManager(self.token_native, self.token_underlying)
        collateral_pool_token_timelock = am.collateral_pool_token_timelock_seconds()
        time.sleep(collateral_pool_token_timelock + 1)

        # get the amount of debt-free pool tokens
        cp = CollateralPool(self.token_native, pool_address)
        cpt = CollateralPoolToken(self.token_native, cp.pool_token())
        debt_free_tokens_UBA = cp.debt_free_tokens_of(self.native_data.address)
        debt_free_tokens = cpt.from_uba(debt_free_tokens_UBA)
        if debt_free_tokens == 0:
            self.logger.info("No debt-free pool tokens available")
        else:
            self.logger.info(f"Debt free pool tokens: {debt_free_tokens}")
            transfer_amount_tokens = min(enter_amount_tokens, debt_free_tokens)
            
            # transfer pool tokens to partner bot
            self.ca.transfer_pool_tokens(
                pool_address, 
                self.partner_native_data.address, 
                transfer_amount_tokens
                )
            self.partner_logger.info(f"Got {transfer_amount_tokens} of pool tokens from user bot.")

            # exit pool from partner bot
            time.sleep(5)
            max_exit_amount = cp.max_amount_to_stay_above_exit_CR(self.token_underlying)
            exit_amount_tokens = min(transfer_amount_tokens, max_exit_amount)
            if max_exit_amount == 0:
                self.partner_logger.info("No collateral can be exited from the pool without going below exit CR.")
            else:
                self.ca_partner.exit_pool(pool_address, exit_amount_tokens, log_steps=True)

        # data for expected_state
        self.pool_address = pool_address
        self.enter_amount_collateral = enter_amount_collateral
        self.enter_amount_tokens = enter_amount_tokens
        if debt_free_tokens > 0:
            self.transfer_amount_tokens = transfer_amount_tokens
            self.exit_amount_tokens = exit_amount_tokens
        else:
            self.transfer_amount_tokens = 0
            self.exit_amount_tokens = 0


    @property
    def expected_state(self):
        # balances
        new_balances = self.balances.copy()
        new_balances[self.token_native] -= self.enter_amount_collateral
        new_balances.subtract_fees(self.ca.fee_tracker)
        # pool holdings
        token_amount = self.enter_amount_tokens - self.transfer_amount_tokens
        new_pool_holdings = self.pool_holdings.copy()
        pool_already_in_holdings = False
        for pool_holding in new_pool_holdings:
            if pool_holding.pool_address == self.pool_address:
                pool_holding.pool_tokens += token_amount
                pool_already_in_holdings = True
                break
        if not pool_already_in_holdings:
            new_pool_holdings.append(PoolHolding(
                pool_address=self.pool_holding.pool_address,
                pool_tokens=token_amount
            ))
        return self.flow_state.replace([new_balances, new_pool_holdings])
    

    @property
    def partner_expected_state(self):
        # balances
        new_balances = self.partner_balances.copy()
        new_balances[self.token_native] += tokens_to_collateral(self.token_native, self.pool_address, self.exit_amount_tokens)
        new_balances.subtract_fees(self.ca_partner.fee_tracker)
        # pool holdings
        new_pool_holdings = self.partner_pool_holdings.copy()
        pool_holding_list = [ph for ph in self.partner_pool_holdings if ph.pool_address == self.pool_address]
        if pool_holding_list:
            pool_holding = pool_holding_list[0]
        else:
            pool_holding = PoolHolding(
                pool_address=self.pool_address,
                pool_tokens=0
            )
        new_token_amount = pool_holding.pool_tokens + self.transfer_amount_tokens - self.exit_amount_tokens
        if new_token_amount == 0 and pool_holding in new_pool_holdings:
            new_pool_holdings.remove(pool_holding)
        else:
            for pool_holding in new_pool_holdings:
                if pool_holding.pool_address == self.pool_address:
                    pool_holding.pool_tokens = new_token_amount
        return self.partner_flow_state.replace([new_balances, new_pool_holdings])