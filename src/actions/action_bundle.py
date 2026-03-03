from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from src.interfaces.contracts.asset_manager import AssetManager
from src.actions.core_actions.core_actions import core_actions
from src.interfaces.user.user_bot import UserBot
from src.interfaces.user.state_manager import StateManager
if TYPE_CHECKING:
    from src.utils.data_structures import FlowState, RelevantInfo, UserData


class ActionBundle(ABC):
    def __init__(
            self,
            user_data: "UserData",
            flow_state : "FlowState",
            cli: bool
        ):

        # sm for data extraction and logging
        self.user_data = user_data
        if cli:
            sm = UserBot(user_data)
            sm_partner = UserBot(user_data.partner_data())
        else:
            sm = StateManager(user_data)
            sm_partner = StateManager(user_data.partner_data())
        
        # tokens
        self.token_native = sm.token_native
        self.token_underlying = sm.token_underlying
        self.token_fasset = sm.token_fasset

        # networks
        self.native_network = sm.native_network
        self.underlying_network = sm.underlying_network
        
        # secrets
        self.native_credentials = sm.native_credentials
        self.underlying_credentials = sm.underlying_credentials
        self.partner_native_credentials = sm_partner.native_credentials
        self.partner_underlying_credentials = sm_partner.underlying_credentials
        
        # loggers
        self.logger = sm.logger
        self.partner_logger = sm_partner.logger

        # state
        self.flow_state = flow_state
        self.balances = flow_state.balances
        self.mint_status = flow_state.mint_status
        self.redemption_status = flow_state.redemption_status
        self.pool_holdings = flow_state.pool_holdings
        
        # flow logic
        self.lot_size = AssetManager(self.native_network, self.token_fasset).lot_size()
        partner_data = user_data.partner_data()
        self.ca = core_actions(user_data, cli)
        self.ca_partner = core_actions(partner_data, cli)
        self.partner_involved = False  # set to True in subclasses where partner is involved

    @abstractmethod
    def condition(self) -> bool:
        pass

    @abstractmethod
    def action(self) -> None:
        pass

    @property
    @abstractmethod
    def expected_state(self) -> "FlowState | list[FlowState]":
        pass

    def general_conditions(self) -> bool:
        enough_native = self.balances[self.token_native] > 10  # to avoid gas issues
        return enough_native
    
    def update_partner_flow_state(self, partner_flow_state : "FlowState") -> None:
        self.partner_flow_state = partner_flow_state
        self.partner_balances = partner_flow_state.balances
        self.partner_mint_status = partner_flow_state.mint_status
        self.partner_redemption_status = partner_flow_state.redemption_status
        self.partner_pool_holdings = partner_flow_state.pool_holdings

    @abstractmethod
    def relevant_info(self) -> "RelevantInfo":
        pass