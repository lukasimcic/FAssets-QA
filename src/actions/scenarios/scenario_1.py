from decimal import Decimal
import random
import time

from src.actions.action_bundle import ActionBundle
from src.actions.helper_functions import can_mint, can_enter_pool, collateral_to_tokens, random_decimal_between, tokens_to_collateral
from src.interfaces.contracts import *
from src.utils.data_storage import DataStorageClient
from src.utils.data_structures import FlowState


class Scenario1(ActionBundle):
    def __init__(self, user_data, flow_state, cli):
        super().__init__(user_data, flow_state, cli)
        self.agents = self.ca.get_agents()


    def condition(self) -> bool:
        enter_pool_condition = can_enter_pool(self.balances, self.token_native)
        mint_condition = can_mint(self.balances, self.token_underlying, self.lot_size, self.agents)
        return enter_pool_condition and mint_condition


    def action(self) -> None:
        # choose agent and pool
        agents = [agent for agent in self.agents if agent.max_lots >= 1]
        agent = random.choice(agents)
        agent_address = agent.address
        pool_address = AgentVault(self.token_native, agent_address, self.native_data).collateral_pool()

        # enter pool
        amount = random_decimal_between(Decimal(1), self.balances[self.token_native])
        token_amount = collateral_to_tokens(self.token_native, pool_address, amount)
        self.ca.enter_pool(pool_address, token_amount, log_steps=True)

        # mint and redeem
        max_lots = [agent.max_lots for agent in self.agents if agent.address == agent_address][0]
        max_amount = min(self.balances[self.token_underlying] // self.lot_size, max_lots)
        lot_amount = random.randint(1, max_amount)
        self.ca.mint(lot_amount, agent=agent_address, log_steps=True)
        time.sleep(10)
        remaining_lots = self.ca.redeem(lot_amount, log_steps=True)

        # wait timelock
        am = AssetManager(self.token_native, self.token_underlying)
        collateral_pool_token_timelock = am.collateral_pool_token_timelock_seconds()
        time.sleep(collateral_pool_token_timelock + 1)

        # exit pool and withdraw all fees
        self.ca.exit_pool(pool_address, token_amount, log_steps=True)
        collateral_amount = tokens_to_collateral(self.token_native, pool_address, token_amount)
        cp = CollateralPool(self.token_native, pool_address)
        fee_amount_uba = cp.fAsset_fees_of(self.native_data.address)
        fee_amount = self.token_fasset.from_uba(fee_amount_uba)
        self.ca.withdraw_pool_fees(pool_address, fee_amount, log_steps=True)

        # data for expected_state
        self.lot_amount = lot_amount
        self.pool_address = pool_address
        self.fee_amount = fee_amount
        self.remaining_lots = remaining_lots
        self.agent = agent
        self.collateral_amount = collateral_amount
        self.amount = amount


    @property
    def expected_state(self) -> list[FlowState]:
        new_balances = self.balances.copy()
        new_balances.subtract_fees(self.ca.fee_tracker)

        # pool fees withdrawal, pool enter and exit
        new_balances[self.token_native] += (self.collateral_amount - self.amount)
        new_balances[self.token_fasset] += self.fee_amount

        # mint and redeem
        new_balances[self.token_underlying] -= self.lot_size * self.lot_amount * (1 + self.agent.fee / 1e2)
        new_balances[self.token_fasset] += self.lot_size * self.lot_amount  
        new_balances[self.token_fasset] -= self.lot_size * (self.lot_amount - self.remaining_lots)
        dsc = DataStorageClient(self.user_data, "redeem")
        redemption_ids = dsc.get_new_record_ids(previous_ids=self.redemption_status.get_all_ids())

        # case 1: redemption not completed yet
        new_balances_1 = new_balances.copy()
        new_redemption_status_1_1 = self.redemption_status.copy()
        new_redemption_status_1_2 = self.redemption_status.copy()
        new_redemption_status_1_1.pending.extend(redemption_ids)
        new_redemption_status_1_2.default.extend(redemption_ids)

        # case 2: redemption completed
        new_balances_2 = new_balances.copy()
        new_redemption_status_2 = self.redemption_status.copy()
        new_redemption_status_2.success.extend(redemption_ids)
        redemption_fee = AssetManager(self.token_native, self.token_underlying).redemption_fee_bips()
        new_balances_2[self.token_underlying] -= self.lot_size * self.lot_amount * (redemption_fee / 1e2)

        # pool holdings
        new_pool_holdings = self.pool_holdings.copy()
        for pool_holding in new_pool_holdings:
            if pool_holding.pool_address == self.pool_address:
                pool_holding.fasset_fees = 0

        return [
            self.flow_state.replace([new_balances_1, new_redemption_status_1_1, new_pool_holdings]),
            self.flow_state.replace([new_balances_1, new_redemption_status_1_2, new_pool_holdings]),
            self.flow_state.replace([new_balances_2, new_redemption_status_2, new_pool_holdings])
            ]
