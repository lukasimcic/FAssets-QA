from src.utils.config import token_fasset, token_underlying, token_native, lot_size
import random

class FlowActions:
    def __init__(self, flow):
        self.flow = flow

    def mint(self):
        lot_amount = random.randint(1, self.flow.balances[token_underlying] // lot_size)
        self.flow.executor.mint(lot_amount, log_steps=self.flow.log_steps, timeout=self.flow.timeout)

    def mint_random(self):
        lot_amount = random.randint(1, self.flow.balances[token_underlying] // lot_size)
        agents = []
        for agent in self.flow.executor.get_agents():
            if agent["max_lots"] * lot_size >= lot_amount:
                agents.append(agent["address"])
        agent = random.choice(agents)
        self.flow.executor.mint(lot_amount, agent=agent, log_steps=self.flow.log_steps, timeout=self.flow.timeout)

    def redeem(self):
        lot_amount = random.randint(1, self.flow.balances[token_fasset] // lot_size)
        self.flow.executor.redeem(lot_amount, log_steps=self.flow.log_steps, timeout=self.flow.timeout)

    def mint_execute(self):
        mint_id = random.choice(self.flow.mint_status["PENDING"])
        self.flow.executor.execute_mint(mint_id, log_steps=self.flow.log_steps, timeout=self.flow.timeout)

    def redeem_default(self):
        redemption_id = random.choice(self.flow.redemption_status["DEFAULT"])
        self.flow.executor.redeem_default(redemption_id, log_steps=self.flow.log_steps, timeout=self.flow.timeout)

    def enter_pool(self):
        pool = random.choice(self.flow.pools)
        amount = random.uniform(0, self.flow.balances[token_native])
        self.flow.executor.enter_pool(pool["Pool address"], amount, log_steps=self.flow.log_steps, timeout=self.flow.timeout)

    def exit_pool(self):
        pool = random.choice(self.flow.pool_holdings)
        amount = random.uniform(0, pool["Pool tokens"])
        self.flow.executor.exit_pool(pool["Pool address"], amount, log_steps=self.flow.log_steps, timeout=self.flow.timeout)

    def withdraw_pool_fees(self):
        pool = random.choice(self.flow.pool_holdings)
        self.flow.executor.withdraw_pool_fees(pool["Pool address"], log_steps=self.flow.log_steps, timeout=self.flow.timeout)

    def scenario_1(self):
        pass # TODO