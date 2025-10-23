from src.interfaces.contracts.asset_manager import AssetManager
from src.interfaces.user.minter import Minter
from src.actions.core_actions.core_actions import CoreActions

class CoreActionsManual(CoreActions):
    def __init__(self, minter : Minter):
        super().__init__()
        self.minter = minter
        self.logger = minter.logger

    def mint(self, lot_amount, agent=None, log_steps=False):
        # TODO if agent is none, choose the best agent with lowesrt fees
        self.logger.info(f"Minting {lot_amount} lots against agent {agent}.")
        self.minter.mint(lot_amount, agent, log_steps=log_steps)

    def redeem(self, lot_amount, log_steps=False):
        self.logger.info(f"Redeeming {lot_amount} lots.")
        pass

    def enter_pool(self, pool_address, amount, log_steps=False):
        self.logger.info(f"Entering pool {pool_address} with amount {amount}.")
        pass

    def exit_pool(self, pool_address, amount, log_steps=False):
        self.logger.info(f"Exiting pool {pool_address} with amount {amount}.")
        pass

    def get_agents(self, chunk_size=10, log_steps=False):
        self.logger.info("Getting available agents.")
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


    def withdraw_pool_fees(self, pool_address, log_steps=False):
        self.logger.info(f"Withdrawing pool fees from pool {pool_address}.")
        pass

    def mint_execute(self, mint_id, log_steps=False):
        self.logger.info(f"Executing minting for mint ID {mint_id}.")
        pass

    def redeem_default(self, redemption_id, log_steps=False):
        self.logger.info(f"Executing redemption for redemption ID {redemption_id}.")
        pass