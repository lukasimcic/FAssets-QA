from src.actions.action_bundle import ActionBundle
from src.actions.helper_functions import can_enter_pool
import random


class EnterRandomPoolRandomAmount(ActionBundle):
    def __init__(self, user_data, flow_state, cli):
        super().__init__(user_data, flow_state, cli)

    def action(self):
        pool = random.choice(self.pools)
        amount = random.uniform(0, self.balances[self.token_native])
        self.ca.enter_pool(pool.address, amount)

    def condition(self):
        return can_enter_pool(self.balances, self.token_underlying)

    @property
    def expected_state(self):
        raise NotImplementedError("State update is not implemented yet.")


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
