from abc import ABC, abstractmethod


class CoreActions(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def mint(self, lot_amount, agent=None, log_steps=False):
        """
        Mint lot_amount lots against the specified agent.
        If agent is None, the agent with lowest fees will be used.
        """
        pass

    @abstractmethod
    def redeem(self, lot_amount, log_steps=False):
        """
        Redeem lot_amount lots.
        """
        pass

    @abstractmethod
    def get_agents(self, log_steps=False):
        """
        Get a list of available agents.
        Each agent is represented as a dictionary with keys "address", "max_lots", "fee".
        """
        pass

    @abstractmethod
    def enter_pool(self, pool_address, amount, log_steps=False):
        """
        Enter the specified pool with the given amount.
        """
        pass

    @abstractmethod
    def exit_pool(self, pool_address, amount, log_steps=False):
        """
        Exit the specified pool with the given amount.
        """
        pass

    @abstractmethod
    def withdraw_pool_fees(self, pool_address, log_steps=False):
        """
        Withdraw all fees from the specified pool.
        """
        pass

    @abstractmethod
    def mint_execute(self, mint_id, log_steps=False):
        """
        Execute the mint with the given mint id.
        """
        pass

    @abstractmethod
    def redeem_default(self, redemption_id, log_steps=False):
        """
        Redeem the defaulted redemption with the given redemption id.
        """
        pass