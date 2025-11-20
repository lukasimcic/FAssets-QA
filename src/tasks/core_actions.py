from src.interfaces.user.informer import Informer
from src.interfaces.contracts.asset_manager import AssetManager
from src.interfaces.user.minter import Minter
from src.interfaces.user.redeemer import Redeemer
from src.interfaces.user.pool_manager import PoolManager
from config.config_qa import zero_address

class CoreActions():
    def __init__(self, user_data):
        self.informer = Informer(**user_data)
        self.minter = Minter(**user_data)
        self.redeemer = Redeemer(**user_data)
        self.pool_manager = PoolManager(**user_data)
        self.logger = self.informer.logger

    def get_balances(self):
        balances = self.informer.get_balances()
        self.logger.info(f"Balances: {balances}")
        return balances

    def get_pools(self):
        self.logger.info("Pools:")
        pass

    def get_pool_holdings(self):
        self.logger.info("Pool holdings:")
        pass

    def get_mint_status(self):
        mint_status = self.minter.mint_status()
        self.logger.info(f"Mint status: {mint_status}")
        return mint_status

    def get_redemption_status(self):
        redemption_status = self.redeemer.redemption_status()
        self.logger.info(f"Redemption status: {redemption_status}")
        return redemption_status

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

    def withdraw_pool_fees(self, pool_address, fees, log_steps=False):
        self.logger.info(f"Withdrawing pool fees from pool {pool_address}.")
        self.pool_manager.withdraw_pool_fees(pool_address, fees, log_steps=log_steps)

    def mint_execute(self, mint_id, log_steps=False):
        self.logger.info(f"Executing minting for mint ID {mint_id}.")
        self.minter.prove_and_execute_minting(mint_id, log_steps=log_steps)

    def redeem_default(self, redemption_id, log_steps=False):
        self.logger.info(f"Executing redemption for redemption ID {redemption_id}.")
        self.redeemer.redeem_default(redemption_id, log_steps=log_steps)