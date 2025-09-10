from utils.user_bot import UserBot
from utils.config import *
import random
import time
import threading

class Flow:
    """
    This class demonstrates a flow of a user bot.
    When calling flow.run(), it will repeatedly choose at random one of the following actions, if possible:
        - mint: Mint a random amount of lots against an agent with lowest fee.
        - mint_random: Mint a random amount of lots against a random agent.
        - redeem: Redeem a random amount of lots.
        - mint_execute: Execute a pending mint.
        - redeem_default: Redeem a default redemption.
        - enter_pool: Enter a random pool with a random amount.
        - exit_pool: Exit a random (valid) pool with a random amount.
        - withdraw_pool_fees: Withdraws the fees from a random (valid) pool.
        - scenario_1: TODO
    """
    def __init__(
        self,
        token_fasset,
        num=0, 
        actions=[],
        log_steps=True, config=None, total_time=None, time_wait=60, timeout=None
    ):
        self.executor = UserBot(token_fasset, num, config)
        self.log_steps = log_steps
        self.total_time = total_time
        self.time_wait = time_wait
        self.timeout = timeout
        self.actions = [(getattr(self, f"_can_{name}"), getattr(self, f"_{name}")) for name in actions]

    def _can_mint(self):
        return self.balances[token_underlying] >= lot_size
    
    def _can_mint_random(self):
        return self._can_mint()
    
    def _can_redeem(self):
        return self.balances[token_fasset] >= lot_size
    
    def _can_mint_execute(self):
        return self.mint_status["PENDING"]

    def _can_redeem_default(self):
        return self.redemption_status["DEFAULT"]
    
    def _can_enter_pool(self):
        return self.pools and self.balances[token_underlying] > 0
    
    def _can_exit_pool(self):
        return self.pool_holdings
    
    def _can_withdraw_pool_fees(self):
        return self.pool_holdings

    def _can_scenario_1(self):
        pass # TODO

    def _mint(self):
        lot_amount = random.randint(1, self.balances[token_underlying] // lot_size)
        self.executor.mint(lot_amount, log_steps=self.log_steps, timeout=self.timeout)

    def _mint_random(self):
        lot_amount = random.randint(1, self.balances[token_underlying] // lot_size)
        agents = []
        for agent in self.executor.get_agents():
            if agent["max_lots"] * lot_size >= lot_amount:
                agents.append(agent["address"])
        agent = random.choice(agents)
        self.executor.mint(lot_amount, agent=agent, log_steps=self.log_steps, timeout=self.timeout)

    def _redeem(self):
        lot_amount = random.randint(1, self.balances[token_fasset] // lot_size)
        self.executor.redeem(lot_amount, log_steps=self.log_steps, timeout=self.timeout)

    def _mint_execute(self):
        mint_id = random.choice(self.mint_status["PENDING"])
        self.executor.execute_mint(mint_id, log_steps=self.log_steps, timeout=self.timeout)

    def _redeem_default(self):
        redemption_id = random.choice(self.redemption_status["DEFAULT"])
        self.executor.redeem_default(redemption_id, log_steps=self.log_steps, timeout=self.timeout)

    def _enter_pool(self):
        pool = random.choice(self.pools)
        amount = random.uniform(0, self.balances[token_native])
        self.executor.enter_pool(pool["Pool address"], amount, log_steps=self.log_steps, timeout=self.timeout)

    def _exit_pool(self):
        pool = random.choice(self.pool_holdings)
        amount = random.uniform(0, pool["Pool tokens"])
        self.executor.exit_pool(pool["Pool address"], amount, log_steps=self.log_steps, timeout=self.timeout)

    def _withdraw_pool_fees(self):
        pool = random.choice(self.pool_holdings)
        self.executor.withdraw_pool_fees(pool["Pool address"], log_steps=self.log_steps, timeout=self.timeout)

    def _scenario_1(self):
        pass # TODO

    def _step(self):
        self.balances = self.executor.get_balances(timeout=self.timeout)
        self.mint_status = self.executor.get_mint_status(timeout=self.timeout)
        self.redemption_status = self.executor.get_redemption_status(timeout=self.timeout)
        self.pools = self.executor.get_pools(timeout=self.timeout)
        self.pool_holdings = self.executor.get_pool_holdings(timeout=self.timeout)

        actions = [logic for condition, logic in self.actions if condition()]
        action = random.choice(actions) if actions else None
        if action:
            action()
        
    def run(self):
        self.executor.logger.info(f"----- Starting flow. -----")
        t = time.time()
        while True:
            self._step()
            time.sleep(self.time_wait)
            if self.total_time:
                self.total_time -= time.time() - t
                if self.total_time <= 0:
                    self.executor.logger.info("--- Total time reached, stopping flow. ---")
                    break
                else:
                    self.executor.logger.info(f"--- Step finished, time left: {self.total_time:.2f} seconds. ---")

if __name__ == "__main__":

    all_actions = ["mint", "mint_random", "redeem", "mint_execute", "redeem_default", "enter_pool", "exit_pool", "withdraw_pool_fees"]
    bot_actions = [all_actions for _ in range(num_user_bots)] # can customize actions for each bot here
    
    threads = []
    for i in range(num_user_bots):
        actions = bot_actions[i]
        flow = Flow(token_fasset, num=i, actions=actions, total_time=300)
        t = threading.Thread(target=flow.run)
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()
