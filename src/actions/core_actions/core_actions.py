from decimal import Decimal
from abc import ABC, abstractmethod
from src.flow.fee_tracker import FeeTracker
from src.utils.data_structures import AgentInfo, Balances, Pool, PoolHolding, RedemptionStatus, MintStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.actions.core_actions.core_actions_cli import CoreActionsCLI
    from src.actions.core_actions.core_actions_manual import CoreActionsManual


class CoreActions(ABC):
    def __init__(self):
        self.fee_tracker = FeeTracker()

    # state (user-specific) retrieval

    @abstractmethod
    def get_balances(self, log_steps: bool = False) -> Balances:
        pass

    @abstractmethod
    def get_mint_status(self, log_steps: bool = False) -> MintStatus:
        pass

    @abstractmethod
    def get_redemption_status(self, log_steps: bool = False) -> RedemptionStatus:
        pass

    @abstractmethod
    def get_pool_holdings(self, log_steps: bool = False) -> list[PoolHolding]:
        pass

    # info (system-specific) retrieval

    @abstractmethod
    def get_agents(self, log_steps: bool = False) -> list[AgentInfo]:
        pass

    @abstractmethod
    def get_pools(self, log_steps: bool = False) -> list[Pool]:
        pass

    # logging

    @abstractmethod
    def log(self, message):
        pass

    # actions implementation

    @abstractmethod
    def mint(self, lot_amount: int, agent: str = None, log_steps: bool = False) -> None:
        pass

    @abstractmethod
    def redeem(self, lot_amount: int, log_steps: bool = False) -> None:
        pass

    @abstractmethod
    def enter_pool(self, pool_address: str, amount: Decimal, log_steps: bool = False) -> None:
        pass

    @abstractmethod
    def exit_pool(self, pool_address: str, amount: Decimal, log_steps: bool = False) -> None:
        pass

    @abstractmethod
    def withdraw_pool_fees(self, pool_address: str, log_steps: bool = False) -> None:
        pass

    @abstractmethod
    def mint_execute(self, mint_id: int, log_steps: bool = False) -> None:
        pass

    @abstractmethod
    def redeem_default(self, redemption_id: int, log_steps: bool = False) -> None:
        pass


def core_actions(user_data, cli: bool = False) -> "CoreActionsManual | CoreActionsCLI":
    if cli:
        from src.actions.core_actions.core_actions_cli import CoreActionsCLI
        return CoreActionsCLI(user_data)
    else:
        from src.actions.core_actions.core_actions_manual import CoreActionsManual
        return CoreActionsManual(user_data)