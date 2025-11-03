from abc import ABC, abstractmethod
from typing import Callable
from src.interfaces.user.informer import Informer
from src.actions.core_actions.core_actions import CoreActions

class ActionBundle(ABC):
    def __init__(
            self,
            ca : CoreActions,
            ca_partner : CoreActions,
            informer : Informer,
            informer_partner : Informer,
            lot_size : int,
            state : dict
        ):
        # core actions
        self.ca = ca
        self.ca_partner = ca_partner
        # lot size
        self.lot_size = lot_size
        # state
        self.state = state
        self.balances = state["balances"]
        self.mint_status = state["mint_status"]
        self.redemption_status = state["redemption_status"]
        self.pools = state["pools"]
        self.pool_holdings = state["pool_holdings"]
        # tokens
        self.token_native = informer.token_native
        self.token_underlying = informer.token_underlying
        self.token_fasset = informer.token_fasset
        # secrets
        self.native_address = informer.native_data["address"]
        self.native_private_key = informer.native_data["private_key"]
        self.underlying_private_key = informer.underlying_data["private_key"]
        self.underlying_public_key = informer.underlying_data["public_key"]
        self.partner_native_address = informer_partner.native_data["address"]
        self.partner_native_private_key = informer_partner.native_data["private_key"]
        self.partner_underlying_private_key = informer_partner.underlying_data["private_key"]
        self.partner_underlying_public_key = informer_partner.underlying_data["public_key"]
        # loggers
        self.logger = informer.logger
        self.partner_logger = informer_partner.logger

    @property
    @abstractmethod
    def action(self):
        pass

    @property
    @abstractmethod
    def condition(self):
        pass

    @property
    def state_before(self):
        return self.state

    @property
    @abstractmethod
    def state_after(self):
        pass
