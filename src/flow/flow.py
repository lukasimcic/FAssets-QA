from src.interfaces.user.user import User
from src.actions import ACTION_BUNDLE_CLASSES
from abc import ABC, abstractmethod
import random
import time

class Flow(ABC):
    """
    This is the base class for flow implementations.
    In a flow, user actions are repeatedly chosen at random among a set of possible actions, if their conditions are met.
    """
    def __init__(
        self,
        actions,
        total_time=None, 
        time_wait=60
    ):
        self.actions = actions
        self.total_time = total_time
        self.time_wait = time_wait

        # flow state
        self.balances = None
        self.mint_status = None
        self.redemption_status = None
        self.pools = None
        self.pool_holdings = None

        # to be defined in subclasses
        self.ca = None
        self.ca_partner = None
        self.informer = None
        self.informer_partner = None
        self.lot_size = None

    def log(self, message, both=True):
        self.informer.logger.info(message)
        if both:
            self.informer_partner.logger.info(message)

    @abstractmethod
    def get_balances(self, log_steps=False):
        pass

    @abstractmethod
    def get_mint_status(self, log_steps=False):
        pass

    @abstractmethod
    def get_redemption_status(self, log_steps=False):
        pass

    @abstractmethod
    def get_pools(self, log_steps=False):
        pass

    @abstractmethod
    def get_pool_holdings(self, log_steps=False):
        pass

    def _step(self):
        state = {
            "balances": self.get_balances(),
            "mint_status": self.get_mint_status(),
            "redemption_status": self.get_redemption_status(),
            "pools": self.get_pools(),
            "pool_holdings": self.get_pool_holdings()
        }

        action_bundles = []
        for cls in ACTION_BUNDLE_CLASSES:
            if cls.__name__ in self.actions:
                bundle = cls(
                        self.ca, 
                        self.ca_partner,
                        self.informer,
                        self.informer_partner,
                        self.lot_size,
                        state
                    )
                if bundle.condition():
                    action_bundles.append(bundle)
        
        bundle = random.choice(action_bundles) if action_bundles else None
        if bundle:
            self.log(f"-- Executing action {bundle.__class__.__name__} --", both=False)
            bundle.action()

    def run(self):
        self.log(f"----- Starting flow. -----")
        t = time.time()
        while True:
            self._step()
            time.sleep(self.time_wait)
            if self.total_time:
                self.total_time -= time.time() - t
                if self.total_time <= 0:
                    self.log("--- Total time reached, stopping flow. ---")
                    break
                else:
                    self.log(f"--- Step finished, time left: {self.total_time:.2f} seconds. ---")