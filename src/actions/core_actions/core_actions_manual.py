from decimal import Decimal
from typing import Literal
import toml
from src.actions.core_actions.core_actions import CoreActions
from src.interfaces.contracts.asset_manager import AssetManager
from src.interfaces.user.state_manager import StateManager
from src.interfaces.user.minter import Minter
from src.interfaces.user.redeemer import Redeemer
from src.interfaces.user.pool_manager import PoolManager
from src.utils.data_structures import AgentInfo, Balances, MintStatus, RedemptionStatus, UserData, Pool, PoolHolding

config = toml.load("config.toml")
zero_address = config["network"]["zero_address"]


class CoreActionsManual(CoreActions):
    def __init__(self, user_data : UserData):
        super().__init__()
        self.sm = StateManager(user_data, fee_tracker=self.fee_tracker)
        self.minter = Minter(user_data, fee_tracker=self.fee_tracker)
        self.redeemer = Redeemer(user_data, fee_tracker=self.fee_tracker)
        self.pool_manager = PoolManager(user_data, fee_tracker=self.fee_tracker)
        self.logger = self.sm.logger

    # state retrieval

    def get_balances(self, log_steps: bool = False) -> Balances:
        balances = self.sm.get_balances(log_steps=log_steps)
        if log_steps:
            self.logger.info(f"Balances: {balances}")
        return balances

    def get_pools(self, log_steps: bool = False) -> list[Pool]:
        pools = self.pool_manager.pools(log_steps=log_steps)
        if log_steps:
            self.logger.info(f"Pools: {pools}")
        return pools

    def get_pool_holdings(self, log_steps: bool = False) -> list[PoolHolding]:
        pool_holdings = self.pool_manager.pool_holdings(log_steps=log_steps)
        if log_steps:
            self.logger.info(f"Pool holdings: {pool_holdings}")
        return pool_holdings
    
    def get_mint_status(self, log_steps: bool = False) -> MintStatus:
        mint_status = self.minter.mint_status()
        if log_steps:
            self.logger.info(f"Mint status: {mint_status}")
        return mint_status

    def get_redemption_status(self, log_steps: bool = False) -> RedemptionStatus:
        redemption_status = self.redeemer.redemption_status()
        if log_steps:
            self.logger.info(f"Redemption status: {redemption_status}")
        return redemption_status
    
    def get_agents(self, chunk_size: int = 10, log_steps: bool = False) -> list[AgentInfo]:
        agent_list = []
        start = 0
        am = AssetManager(self.sm.token_native, self.sm.token_underlying)
        while True:
            new = am.get_available_agents_detailed_list(start, start + chunk_size)
            agent_list.extend(new)
            if len(new) < chunk_size:
                break
            start += len(new)
        fields_mapping = {
            "agentVault": "address",
            "freeCollateralLots": "max_lots",
            "feeBIPS": "fee",
            }
        result = []
        for agent in agent_list:
            d = {}
            for k, v in agent.items():
                if k in fields_mapping:
                    if k.endswith("BIPS"):
                        d[fields_mapping[k]] = Decimal(v / 1e4)
                    else:
                        d[fields_mapping[k]] = v
            result.append(AgentInfo(**d))
        return result
    
    # logic

    def log(self, message: str, level: Literal["info", "warning", "error"]) -> None:
        return self.sm.log_step(message, True, level)

    # actions implementation

    def mint(self, lot_amount: int, agent: str = None, log_steps: bool = False) -> None:
        self.logger.info(f"Minting {lot_amount} lots against agent {agent}.")
        mint_id = self.minter.mint(lot_amount, agent, log_steps=log_steps)
        self.logger.info(f"Proving underlying payment and executing minting.")
        self.minter.prove_and_execute_minting(mint_id, log_steps=log_steps)

    def redeem(self, lot_amount: int, executor: str = zero_address, executor_fee: Decimal = Decimal(0), log_steps: bool = False) -> int:
        self.logger.info(f"Redeeming {lot_amount} lots.")
        remaining_lots = self.redeemer.redeem(
            lots=lot_amount, 
            executor=executor, 
            executor_fee=executor_fee,
            log_steps=log_steps
        )
        self.logger.info(f"Redeemed {lot_amount - remaining_lots} lots.")
        return remaining_lots

    def enter_pool(self, pool_address: str, amount: Decimal, log_steps: bool = False) -> None:
        self.logger.info(f"Entering pool {pool_address} with amount {amount}.")
        self.pool_manager.enter_pool(pool_address, amount, log_steps=log_steps)

    def exit_pool(self, pool_address: str, amount: Decimal, log_steps: bool = False) -> None:
        self.logger.info(f"Exiting pool {pool_address} with amount {amount}.")
        self.pool_manager.exit_pool(pool_address, amount, log_steps=log_steps)

    def withdraw_pool_fees(self, pool_address: str, fees: Decimal, log_steps: bool = False) -> None:
        self.logger.info(f"Withdrawing pool {fees} fees from pool {pool_address}.")
        self.pool_manager.withdraw_pool_fees(pool_address, fees, log_steps=log_steps)

    def transfer_pool_tokens(self, pool_address: str, to_address: str, amount: Decimal, log_steps: bool = False) -> None:
        self.logger.info(f"Transferring {amount} pool tokens of pool {pool_address} to {to_address}.")
        self.pool_manager.transfer_pool_tokens(pool_address, to_address, amount, log_steps=log_steps)

    def mint_execute(self, mint_id: int, log_steps: bool = False) -> None:
        self.logger.info(f"Executing minting for mint ID {mint_id}.")
        self.minter.prove_and_execute_minting(mint_id, log_steps=log_steps)

    def redeem_default(self, redemption_id: int, log_steps: bool = False) -> None:
        self.logger.info(f"Executing redemption for redemption ID {redemption_id}.")
        self.redeemer.redeem_default(redemption_id, log_steps=log_steps)