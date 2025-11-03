from src.interfaces.user.redeemer import Redeemer
from src.flow.flow import Flow
from src.actions.core_actions.core_actions_manual import CoreActionsManual
from src.interfaces.contracts.fasset import FAsset
from src.interfaces.network.network import Network
from src.interfaces.contracts.asset_manager import AssetManager
from src.interfaces.user.user import User
from src.interfaces.user.minter import Minter
from src.interfaces.user.informer import Informer

class FlowManual(Flow):
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
        - scenario_1: Enter a pool, mint and redeem lots, wait for the pool token timelock, then exit the pool and withdraw pool fees if possible.
        - scenario_2: Enter a pool, wait for the pool token timelock, transfer debt-free pool tokens to the partner bot, and have the partner bot exit the pool.
    """
    def __init__(
        self,
        token_underlying,
        actions,
        num=0, 
        config=None, total_time=None, time_wait=60
    ):
        super().__init__(actions, total_time, time_wait)

        # info
        self.informer = Informer(token_underlying, num)
        self.informer_partner = Informer(token_underlying, num, partner=True)
        self.logger = self.informer.logger
        self.partner_logger = self.informer_partner.logger

        # tokens
        self.token_native = self.informer.token_native
        self.token_underlying = self.informer.token_underlying
        self.token_fasset = self.informer.token_fasset
        
        # users
        self.minter = Minter(self.token_native, token_underlying, num, config=config)
        self.minter_partner = Minter(self.token_native, token_underlying, num, partner=True, config=config)
        self.redeemer = Redeemer(self.token_native, token_underlying, num, config=config)
        self.redeemer_partner = Redeemer(self.token_native, token_underlying, num, partner=True, config=config)
        
        # flow logic
        self.lot_size = AssetManager("", "", token_underlying).lot_size()
        self.ca = CoreActionsManual(self.minter, self.redeemer)
        self.ca_partner = CoreActionsManual(self.minter_partner, self.redeemer_partner)

    def get_balances(self, log_steps=False):
        balances = self.informer.get_balances(log_steps=log_steps)
        self.logger.info(f"Balances: {balances}")
        return balances

    def get_pools(self, log_steps=False):
        self.logger.info("Pools:")
        pass

    def get_pool_holdings(self, log_steps=False):
        self.logger.info("Pool holdings:")
        pass

    def get_mint_status(self, log_steps=False):
        mint_status = self.minter.mint_status()
        self.logger.info(f"Mint status: {mint_status}")
        return mint_status

    def get_redemption_status(self, log_steps=False):
        redemption_status = self.redeemer.redemption_status()
        self.logger.info(f"Redemption status: {redemption_status}")
        return redemption_status