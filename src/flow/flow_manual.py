from src.flow.flow import Flow
from src.actions.core_actions.core_actions_manual import CoreActionsManual
from src.interfaces.contracts.fasset import FAsset
from src.interfaces.networks.network import Network
from src.interfaces.contracts.asset_manager import AssetManager
from src.interfaces.user.user import User
from src.interfaces.user.minter import Minter

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

        # user
        self.user = User(token_underlying, num)
        self.partner = User(token_underlying, num, partner=True)
        self.minter = Minter(token_underlying, num, config=config)
        self.minter_partner = Minter(token_underlying, num, partner=True, config=config)
        self.logger = self.user.logger

        # tokens
        self.token_native = self.user.token_native
        self.token_underlying = self.user.token_underlying
        self.token_fasset = self.user.token_fasset

        # flow logic
        self.lot_size = AssetManager("", "", token_underlying).lot_size()
        self.ca = CoreActionsManual(self.minter)
        self.ca_partner = CoreActionsManual(self.minter_partner)

    def get_balances(self, log_steps=False):
        self.logger.info("Getting balances.")
        nn = Network(
            self.token_native,
            self.user.native_data["address"], 
            self.user.native_data["private_key"]
        )
        un = Network(
            self.token_underlying,
            self.user.underlying_data["public_key"], 
            self.user.underlying_data["private_key"]
        )
        f = FAsset(
            self.user.native_data["address"],
            self.user.native_data["private_key"],
            self.token_underlying)
        balances = {
            self.token_native: float(nn.get_balance()),
            self.token_underlying: float(un.get_balance()),
            self.token_fasset: float(f.get_balance())
        }
        return balances

    def get_pools(self, log_steps=False):
        self.logger.info("Getting pools.")
        pass

    def get_pool_holdings(self, log_steps=False):
        self.logger.info("Getting pool holdings.")
        pass

    def get_mint_status(self, log_steps=False):
        self.logger.info("Getting mint status.")
        pass

    def get_redemption_status(self, log_steps=False):
        self.logger.info("Getting redemption status.")
        pass