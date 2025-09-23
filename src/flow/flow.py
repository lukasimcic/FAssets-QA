from src.interfaces.user_bot import UserBot
from src.flow.flow_conditions import FlowConditions
from src.flow.flow_actions import FlowActions
import random
import time

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
        self.executor = UserBot(token_fasset, num, config=config)
        self.partner_executor = UserBot(token_fasset, num, partner=True, config=config)
        self.total_time = total_time
        self.time_wait = time_wait
        self.timeout = timeout
        self.log_steps = log_steps

        self.balances = None
        self.mint_status = None
        self.redemption_status = None
        self.pools = None
        self.pool_holdings = None

        self.fc = FlowConditions(self)
        self.fa = FlowActions(self)
        self.actions = [(getattr(self.fc, f"can_{name}"), getattr(self.fa, f"{name}")) for name in actions] 

    def _step(self):
        self.balances = self.executor.get_balances()
        self.mint_status = self.executor.get_mint_status()
        self.redemption_status = self.executor.get_redemption_status()
        self.pools = self.executor.get_pools()
        self.pool_holdings = self.executor.get_pool_holdings()

        actions = [logic for condition, logic in self.actions if condition()]
        action = random.choice(actions) if actions else None
        if action:
            self.executor.logger.info(f"-- Executing action {action.__name__} --")
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