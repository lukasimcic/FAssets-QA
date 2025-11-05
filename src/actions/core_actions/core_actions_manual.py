from src.actions.core_actions.core_actions import CoreActions
from src.interfaces.contracts.asset_manager import AssetManager
from src.interfaces.user.minter import Minter
from src.interfaces.user.redeemer import Redeemer
from src.interfaces.user.pool_manager import PoolManager
from config.config_qa import zero_address

class CoreActionsManual(CoreActions):
    def __init__(self, minter : Minter, redeemer : Redeemer, pool_manager : PoolManager):
        super().__init__()
        self.minter = minter
        self.redeemer = redeemer
        self.pool_manager = pool_manager
        self.logger = minter.logger

    def mint(self, lot_amount, agent=None, log_steps=False):
        self.logger.info(f"Minting {lot_amount} lots against agent {agent}.")
        mint_id = self.minter.mint(lot_amount, agent, log_steps=log_steps)
        self.logger.info(f"Proving underlying payment and executing minting.")
        self.minter.prove_and_execute_minting(mint_id, log_steps=log_steps)

    def redeem(self, lot_amount, executor=zero_address, executor_fee=0, log_steps=False):
        self.logger.info(f"Redeeming {lot_amount} lots.")
        remaining_lots = self.redeemer.redeem(
            lots=lot_amount, 
            executor=executor, 
            executor_fee=executor_fee,
            log_steps=log_steps
        )
        self.logger.info(f"Redeemed {lot_amount - remaining_lots} lots.")
        
    def enter_pool(self, pool_address, amount, log_steps=False):
        self.logger.info(f"Entering pool {pool_address} with amount {amount}.")
        self.pool_manager.enter_pool(pool_address, amount, log_steps=log_steps)

    def exit_pool(self, pool_address, amount, log_steps=False):
        self.logger.info(f"Exiting pool {pool_address} with amount {amount}.")
        self.pool_manager.exit_pool(pool_address, amount, log_steps=log_steps)

    def get_agents(self, chunk_size=10, log_steps=False):
        agent_list = []
        start = 0
        am = AssetManager("", "", self.minter.token_underlying)
        while True:
            new = am.get_available_agents_detailed_list(start, start + chunk_size)
            agent_list.extend(new)
            if len(new) < chunk_size:
                break
            start += len(new)
        fields_mapping = {
            "agentVault": "address",
            "freeCollateralLots": "max_lots",
            "feeBIPS": "fee"
            }
        result = []
        for agent in agent_list:
            d = {}
            for k, v in agent.items():
                if k == "feeBIPS":
                    d[fields_mapping[k]] = v / 100  # convert to percentage
                else:
                    d[fields_mapping[k]] = v
            result.append(d)
        return result

    def withdraw_pool_fees(self, pool_address, fees, log_steps=False):
        self.logger.info(f"Withdrawing pool fees from pool {pool_address}.")
        self.pool_manager.withdraw_pool_fees(pool_address, fees, log_steps=log_steps)

    def mint_execute(self, mint_id, log_steps=False):
        self.logger.info(f"Executing minting for mint ID {mint_id}.")
        self.minter.prove_and_execute_minting(mint_id, log_steps=log_steps)

    def redeem_default(self, redemption_id, log_steps=False):
        self.logger.info(f"Executing redemption for redemption ID {redemption_id}.")
        self.redeemer.redeem_default(redemption_id, log_steps=log_steps)