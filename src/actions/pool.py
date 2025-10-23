from src.actions.action_bundle import ActionBundle
import random


def can_enter_pool(balances, token_underlying):
    return token_underlying in balances and balances[token_underlying] > 0


class EnterRandomPoolRandomAmount(ActionBundle):
    def __init__(self, ca, ca_partner, user, partner, lot_size, state):
        super().__init__(ca, ca_partner, user, partner, lot_size, state)

    def action(self):
        pool = random.choice(self.pools)
        amount = random.uniform(0, self.balances[self.token_native])
        self.ca.enter_pool(pool["Pool address"], amount)

    def condition(self):
        return can_enter_pool(self.balances, self.token_underlying)

    def state_after(self):
        pass # TODO


class ExitRandomPoolRandomAmount(ActionBundle):
    def __init__(self, ca, ca_partner, user, partner, lot_size, state):
        super().__init__(ca, ca_partner, user, partner, lot_size, state)

    def action(self):
        pool = random.choice(self.pool_holdings)
        amount = random.uniform(0, pool["Pool tokens"])
        self.ca.exit_pool(pool["Pool address"], amount)

    def condition(self):
        return self.pool_holdings

    def state_after(self):
        pass # TODO


class WithdrawPoolFeesRandomPool(ActionBundle):
    def __init__(self, ca, ca_partner, user, partner, lot_size, state):
        super().__init__(ca, ca_partner, user, partner, lot_size, state)

    def action(self):
        pool = random.choice(self.pool_holdings)
        self.ca.withdraw_pool_fees(pool["Pool address"])

    def condition(self):
        return self.pool_holdings

    def state_after(self):
        pass # TODO
