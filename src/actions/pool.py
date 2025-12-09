from src.actions.action_bundle import ActionBundle
from src.actions.helper_functions import can_enter_pool, collateral_to_token_share
from src.utils.data_structures import PoolHolding
import random


class EnterRandomPoolRandomAmount(ActionBundle):
    def __init__(self, user_data, flow_state, cli):
        super().__init__(user_data, flow_state, cli)

    def condition(self):
        return can_enter_pool(self.balances, self.token_native)

    def action(self):
        # action logic
        pool = random.choice(self.pools)
        amount = random.uniform(1, self.balances[self.token_native])
        amount = min(amount, 5) # TODO delete
        self.ca.enter_pool(pool.address, amount)
        # data for expected_state
        self.pool = pool
        self.amount = amount

    @property
    def expected_state(self):
        # balances
        new_balances = self.balances.copy()
        new_balances[self.token_native] -= self.amount
        new_balances.subtract_fees(self.ca.fee_tracker)
        # pool holdings
        token_amount = collateral_to_token_share(self.pool.address, self.amount)
        new_pool_holdings = self.pool_holdings.copy()
        pool_already_in_holdings = False
        for pool_holding in new_pool_holdings:
            if pool_holding.pool_address == self.pool.address:
                pool_holding.pool_tokens += token_amount
                pool_already_in_holdings = True
                break
        if not pool_already_in_holdings:
            new_pool_holdings.append(PoolHolding(
                pool_address=self.pool.address,
                pool_tokens=token_amount
            ))
        return self.flow_state.replace([new_balances, new_pool_holdings])


class ExitRandomPoolRandomAmount(ActionBundle):
    def __init__(self, user_data, flow_state, cli):
        super().__init__(user_data, flow_state, cli)

    def action(self):
        pool = random.choice(self.pool_holdings)
        amount = random.uniform(0, pool.pool_tokens)
        self.ca.exit_pool(pool.pool_address, amount)

    def condition(self):
        return self.pool_holdings

    @property
    def expected_state(self):
        raise NotImplementedError("State update is not implemented yet.")


class WithdrawPoolFeesRandomPool(ActionBundle):
    def __init__(self, user_data, flow_state, cli):
        super().__init__(user_data, flow_state, cli)

    def action(self):
        pool = random.choice(self.pool_holdings)
        self.ca.withdraw_pool_fees(pool.pool_address)

    def condition(self):
        return self.pool_holdings

    @property
    def expected_state(self):
        raise NotImplementedError("State update is not implemented yet.")
