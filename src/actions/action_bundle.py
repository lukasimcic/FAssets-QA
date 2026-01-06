from abc import ABC, abstractmethod
from src.interfaces.contracts.asset_manager import AssetManager
from src.actions.core_actions.core_actions_cli import CoreActionsCLI
from src.actions.core_actions.core_actions_manual import CoreActionsManual
from src.interfaces.user.user_bot import UserBot
from src.interfaces.user.informer import Informer
from src.utils.data_structures import FlowState, UserData


class ActionBundle(ABC):
    def __init__(
            self,
            user_data: UserData,
            flow_state : FlowState,
            cli: bool
        ):

        # informer for data extraction and logging
        self.user_data = user_data
        if cli:
            informer = UserBot(user_data)
            informer_partner = UserBot(user_data.partner_data())
        else:
            informer = Informer(user_data)
            informer_partner = Informer(user_data.partner_data())
        
        # tokens
        self.token_native = informer.token_native
        self.token_underlying = informer.token_underlying
        self.token_fasset = informer.token_fasset
        
        # secrets
        self.native_data = informer.native_data
        self.underlying_data = informer.underlying_data
        self.partner_native_data = informer_partner.native_data
        self.partner_underlying_data = informer_partner.underlying_data
        
        # loggers
        self.logger = informer.logger
        self.partner_logger = informer_partner.logger

        # state
        self.flow_state = flow_state
        self.balances = flow_state.balances
        self.mint_status = flow_state.mint_status
        self.redemption_status = flow_state.redemption_status
        self.pool_holdings = flow_state.pool_holdings
        
        # flow logic
        self.lot_size = AssetManager(user_data.token_native, user_data.token_underlying).lot_size()
        partner_data = user_data.partner_data()
        if not cli:
            self.ca = CoreActionsManual(user_data)
            self.ca_partner = CoreActionsManual(partner_data)
        else:
            self.ca = CoreActionsCLI(user_data)
            self.ca_partner = CoreActionsCLI(partner_data)
        self.partner_involved = False  # set to True in subclasses where partner is involved

    @abstractmethod
    def condition(self) -> bool:
        pass

    @abstractmethod
    def action(self) -> None:
        pass

    @property
    @abstractmethod
    def expected_state(self) -> FlowState | list[FlowState]:
        pass

    def general_conditions(self) -> bool:
        enough_native = self.balances[self.token_native] > 10  # to avoid gas issues
        return enough_native
    
    def update_partner_flow_state(self, partner_flow_state : FlowState) -> None:
        self.partner_flow_state = partner_flow_state
        self.partner_balances = partner_flow_state.balances
        self.partner_mint_status = partner_flow_state.mint_status
        self.partner_redemption_status = partner_flow_state.redemption_status
        self.partner_pool_holdings = partner_flow_state.pool_holdings