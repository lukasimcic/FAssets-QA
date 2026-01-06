import random
from decimal import Decimal
from src.interfaces.contracts.collateral_pool import CollateralPool
from src.actions.action_bundle import ActionBundle
from src.actions.helper_functions import random_decimal_between, add_max_amount_to_stay_above_exit_CR, can_enter_pool, collateral_to_tokens, tokens_to_collateral
from src.utils.data_structures import FlowState, PoolHolding


class EnterRandomPoolRandomAmount(ActionBundle):
    def __init__(self, user_data, flow_state, cli):
        super().__init__(user_data, flow_state, cli)

    def condition(self) -> bool:
        return can_enter_pool(self.balances, self.token_native)

    def action(self) -> None:
        # action logic
        pools = self.ca.get_pools()
        pool = random.choice(pools)
        min_amount = CollateralPool.min_nat_to_enter
        amount = random_decimal_between(min_amount, self.balances[self.token_native])
        self.ca.enter_pool(pool.address, amount)
        # data for expected_state
        self.pool = pool
        self.amount = amount

    @property
    def expected_state(self) -> FlowState:
        # balances
        new_balances = self.balances.copy()
        new_balances[self.token_native] -= self.amount
        new_balances.subtract_fees(self.ca.fee_tracker)
        # pool holdings
        token_amount = collateral_to_tokens(self.token_native, self.pool.address, self.amount)
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

    def condition(self) -> bool:
        self.pool_holdings = add_max_amount_to_stay_above_exit_CR(self.pool_holdings, self.token_native, self.token_underlying)
        for pool_holding in self.pool_holdings:
            if pool_holding.max_amount_to_exit > 0:
                return True
        return False

    def action(self) -> None:
        # action logic
        pool_holding = random.choice([ph for ph in self.pool_holdings if ph.max_amount_to_exit > 0])
        amount = random_decimal_between(Decimal(0), min(pool_holding.pool_tokens, pool_holding.max_amount_to_exit))
        self.ca.exit_pool(pool_holding.pool_address, amount)
        # data for expected_state
        self.pool_holding = pool_holding
        self.amount = amount 

    @property
    def expected_state(self) -> FlowState:
        # balances
        new_balances = self.balances.copy()
        new_balances[self.token_native] += tokens_to_collateral(self.token_native, self.pool_holding.pool_address, self.amount)
        new_balances.subtract_fees(self.ca.fee_tracker)
        # pool holdings
        new_pool_holdings = self.pool_holdings.copy()
        new_token_amount = self.pool_holding.pool_tokens - self.amount
        if new_token_amount == 0:
            new_pool_holdings.remove(self.pool_holding)
        else:
            for pool_holding in new_pool_holdings:
                if pool_holding.pool_address == self.pool_holding.pool_address:
                    pool_holding.pool_tokens = new_token_amount
                pool_holding.max_amount_to_exit = None
        return self.flow_state.replace([new_balances, new_pool_holdings])


class WithdrawPoolFeesRandomPool(ActionBundle):
    def __init__(self, user_data, flow_state, cli):
        super().__init__(user_data, flow_state, cli)

    def condition(self) -> bool:
        return [ph for ph in self.pool_holdings if ph.fasset_fees > 0]

    def action(self) -> None:
        # action logic
        pool_holding = random.choice([ph for ph in self.pool_holdings if ph.fasset_fees > 0])
        fees = pool_holding.fasset_fees
        fees_uba = self.token_fasset.to_uba(fees)
        amount_uba = random.randint(1, fees_uba)
        amount = self.token_fasset.from_uba(amount_uba)
        self.ca.withdraw_pool_fees(pool_holding.pool_address, amount)
        # data for expected_state
        self.pool_address = pool_holding.pool_address
        self.amount = amount

    @property
    def expected_state(self) -> FlowState:
        # balances
        new_balances = self.balances.copy()
        new_balances[self.token_fasset] += self.amount
        new_balances.subtract_fees(self.ca.fee_tracker)
        # fees
        new_pool_holdings = self.pool_holdings.copy()
        for pool_holding in new_pool_holdings:
            if pool_holding.pool_address == self.pool_address:
                pool_holding.fasset_fees -= self.amount
        return self.flow_state.replace([new_balances, new_pool_holdings])
