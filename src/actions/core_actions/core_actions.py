from src.utils.fee_tracker import FeeTracker
from src.utils.data_structures import AgentInfo, Balances, Pool, PoolHolding, RedemptionStatus, MintStatus
from abc import ABC, abstractmethod



class CoreActions(ABC):
    def __init__(self):
        self.fee_tracker = FeeTracker()

    # state (user-specific) retrieval

    @abstractmethod
    def get_balances(self, log_steps=False) -> Balances:
        pass

    @abstractmethod
    def get_mint_status(self, log_steps=False) -> MintStatus:
        pass

    @abstractmethod
    def get_redemption_status(self, log_steps=False) -> RedemptionStatus:
        pass

    @abstractmethod
    def get_pool_holdings(self, log_steps=False) -> list[PoolHolding]:
        pass

    # info (system-specific) retrieval

    @abstractmethod
    def get_agents(self, log_steps=False) -> list[AgentInfo]:
        pass

    @abstractmethod
    def get_pools(self, log_steps=False) -> list[Pool]:
        pass

    # logging

    @abstractmethod
    def log(self, message):
        pass

    # actions implementation

    @abstractmethod
    def mint(self, lot_amount, agent=None, log_steps=False):
        pass

    @abstractmethod
    def redeem(self, lot_amount, log_steps=False):
        pass

    @abstractmethod
    def enter_pool(self, pool_address, amount, log_steps=False):
        pass

    @abstractmethod
    def exit_pool(self, pool_address, amount, log_steps=False):
        pass

    @abstractmethod
    def withdraw_pool_fees(self, pool_address, log_steps=False):
        pass

    @abstractmethod
    def mint_execute(self, mint_id, log_steps=False):
        pass

    @abstractmethod
    def redeem_default(self, redemption_id, log_steps=False):
        pass