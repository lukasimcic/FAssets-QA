import random
import time
from typing import TYPE_CHECKING
from src.actions.action_bundle import ActionBundle
from src.actions.helper_functions import can_mint
from src.actions.bridge import BRIDGE_FEE
from src.interfaces.contracts import *
from src.utils.data_structures import RelevantInfo
from src.utils.data_storage import DataStorageClient
if TYPE_CHECKING:
    from interfaces.network.tokens import TokenExternalFAsset
    from src.utils.data_structures import UserData
    from src.utils.data_structures import FlowState

# TODO: remove caps also at bridge.py

class ScenarioMintBridge(ActionBundle):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool, token_external: "TokenExternalFAsset"):
        if cli:
            raise Exception(f"{self.__class__.__name__} is not available in CLI mode.")
        super().__init__(user_data, flow_state, cli)
        self.token_external = token_external
        self.external_network = token_external.network

    def condition(self) -> bool:
        self.agents_dict = self.ca.get_agents()
        mint_condition = can_mint(self.balances, self.token_underlying, self.lot_size, self.agents_dict)
        bridge_to_condition = self.balances[self.token_native] >= BRIDGE_FEE[self.token_native]
        return mint_condition and bridge_to_condition

    def action(self) -> None:
        # mint
        agents = [agent for agent in self.agents_dict if agent.max_lots >= 1]
        agent = random.choice(agents)
        possible_lots = int(self.balances[self.token_underlying] // self.lot_size)
        max_lots = min(agent.max_lots, possible_lots)
        lot_amount = min(random.randint(1, max_lots), 5)
        self.ca.mint(lot_amount, agent=agent.address, log_steps=True)

        # bridge
        self.ca.bridge_to(self.external_network, lot_amount, log_steps=True)
        time.sleep(60 * 5)

        # data for expected_state
        self.lot_amount = lot_amount
        self.agent = agent

    @property
    def expected_state(self) -> "FlowState":
        # balances
        new_balances = self.balances.copy()
        new_balances[self.token_underlying] -= self.lot_size * self.lot_amount * (1 + self.agent.fee)
        new_balances[self.token_external] += self.lot_size * self.lot_amount
        new_balances.subtract_fees(self.ca.fee_tracker)
        return self.flow_state.replace([new_balances])
    
    def relevant_info(self) -> "RelevantInfo":
        return RelevantInfo(
            tokens=[self.token_underlying, self.token_native, self.token_fasset, self.token_external, self.external_network.coin],
            mint_status=True
        )
    

class ScenarioMintBridgeBridge(ActionBundle):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool, token_external: "TokenExternalFAsset"):
        if cli:
            raise Exception(f"{self.__class__.__name__} is not available in CLI mode.")
        super().__init__(user_data, flow_state, cli)
        self.token_external = token_external
        self.external_network = token_external.network
    
    def condition(self) -> bool:
        self.agents_dict = self.ca.get_agents()
        mint_condition = can_mint(self.balances, self.token_underlying, self.lot_size, self.agents_dict)
        bridge_to_condition = self.balances[self.token_native] >= BRIDGE_FEE[self.token_native]
        bridge_from_condition = self.balances[self.external_network.coin] >= BRIDGE_FEE[self.external_network.coin]
        return mint_condition and bridge_to_condition and bridge_from_condition
    
    def action(self) -> None:
        # mint
        agents = [agent for agent in self.agents_dict if agent.max_lots >= 1]
        agent = random.choice(agents)
        possible_lots = int(self.balances[self.token_underlying] // self.lot_size)
        max_lots = min(agent.max_lots, possible_lots)
        lot_amount = min(random.randint(1, max_lots), 5)
        self.ca.mint(lot_amount, agent=agent.address, log_steps=True)

        # bridge to external network
        self.ca.bridge_to(self.external_network, lot_amount, log_steps=True)
        time.sleep(60 * 5)

        # bridge from external network
        self.ca.bridge_from(self.external_network, lot_amount, log_steps=True)
        time.sleep(60 * 5)

        # data for expected_state
        self.lot_amount = lot_amount
        self.agent = agent

    @property
    def expected_state(self) -> "FlowState":
        # balances
        new_balances = self.balances.copy()
        new_balances[self.token_underlying] -= self.lot_size * self.lot_amount * (1 + self.agent.fee)
        new_balances[self.token_fasset] += self.lot_size * self.lot_amount
        new_balances.subtract_fees(self.ca.fee_tracker)
        return self.flow_state.replace([new_balances])

    def relevant_info(self) -> "RelevantInfo":
        return RelevantInfo(
            tokens=[self.token_underlying, self.token_native, self.token_fasset, self.token_external, self.external_network.coin],
            mint_status=True
        )
    

class ScenarioMintBridgeBridgeRedeem(ActionBundle):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool, token_external: "TokenExternalFAsset"):
        if cli:
            raise Exception(f"{self.__class__.__name__} is not available in CLI mode.")
        super().__init__(user_data, flow_state, cli)
        self.token_external = token_external
        self.external_network = token_external.network
    
    def condition(self) -> bool:
        self.agents_dict = self.ca.get_agents()
        mint_condition = can_mint(self.balances, self.token_underlying, self.lot_size, self.agents_dict)
        bridge_to_condition = self.balances[self.token_native] >= BRIDGE_FEE[self.token_native]
        bridge_from_condition = self.balances[self.external_network.coin] >= BRIDGE_FEE[self.external_network.coin]
        return mint_condition and bridge_to_condition and bridge_from_condition

    def action(self) -> None:
        # mint
        agents = [agent for agent in self.agents_dict if agent.max_lots >= 1]
        agent = random.choice(agents)
        possible_lots = int(self.balances[self.token_underlying] // self.lot_size)
        max_lots = min(agent.max_lots, possible_lots)
        lot_amount = min(random.randint(1, max_lots), 5)
        self.ca.mint(lot_amount, agent=agent.address, log_steps=True)

        # bridge to external network
        self.ca.bridge_to(self.external_network, lot_amount, log_steps=True)
        time.sleep(60 * 5)

        # bridge from external network
        self.ca.bridge_from(self.external_network, lot_amount, log_steps=True)
        time.sleep(60 * 5)

        # redeem
        remaining_lots = self.ca.redeem(lot_amount, log_steps=True)

        # data for expected_state
        self.lot_amount = lot_amount
        self.agent = agent
        self.remaining_lots = remaining_lots

    @property
    def expected_state(self) -> "FlowState":
        # balances
        new_balances = self.balances.copy()
        new_balances[self.token_underlying] -= self.lot_size * self.lot_amount * (1 + self.agent.fee)
        new_balances[self.token_fasset] += self.lot_size * self.remaining_lots
        new_balances.subtract_fees(self.ca.fee_tracker)
        # redemption status
        new_redemption_status = self.redemption_status.copy()
        dsc = DataStorageClient(self.user_data, "redeem")
        redemption_ids = dsc.get_new_record_ids(previous_ids=new_redemption_status.get_all_ids())
        new_redemption_status.pending.extend(redemption_ids)
        return self.flow_state.replace([new_balances, new_redemption_status])

    def relevant_info(self) -> "RelevantInfo":
        return RelevantInfo(
            tokens=[self.token_underlying, self.token_native, self.token_fasset, self.token_external, self.external_network.coin],
            mint_status=True,
            redemption_status=True
        )


class ScenarioMintBridgeAutoRedeem(ActionBundle):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool, token_external: "TokenExternalFAsset"):
        if cli:
            raise Exception(f"{self.__class__.__name__} is not available in CLI mode.")
        super().__init__(user_data, flow_state, cli)
        self.token_external = token_external
        self.external_network = token_external.network
    
    def condition(self) -> bool:
        self.agents_dict = self.ca.get_agents()
        mint_condition = can_mint(self.balances, self.token_underlying, self.lot_size, self.agents_dict)
        bridge_to_condition = self.balances[self.token_native] >= BRIDGE_FEE[self.token_native]
        auto_redeem_condition = self.balances[self.external_network.coin] >= BRIDGE_FEE[self.external_network.coin]
        return mint_condition and bridge_to_condition and auto_redeem_condition
    
    def action(self) -> None:
        # mint
        agents = [agent for agent in self.agents_dict if agent.max_lots >= 1]
        agent = random.choice(agents)
        possible_lots = int(self.balances[self.token_underlying] // self.lot_size)
        max_lots = min(agent.max_lots, possible_lots)
        lot_amount = min(random.randint(1, max_lots), 5)
        self.ca.mint(lot_amount, agent=agent.address, log_steps=True)

        # bridge to external network
        self.ca.bridge_to(self.external_network, lot_amount, log_steps=True)
        time.sleep(60 * 5)

        # auto-redeem from external network
        self.ca.auto_redeem_from(self.external_network, lot_amount, log_steps=True)
        time.sleep(60 * 5)

        # data for expected_state
        self.lot_amount = lot_amount
        self.agent = agent

    @property
    def expected_state(self) -> "FlowState":
        # balances
        new_balances = self.balances.copy()
        new_balances[self.token_underlying] -= self.lot_size * self.lot_amount * self.agent.fee
        new_balances.subtract_fees(self.ca.fee_tracker)
        return self.flow_state.replace([new_balances])

    def relevant_info(self) -> "RelevantInfo":
        return RelevantInfo(
            tokens=[self.token_underlying, self.token_native, self.token_fasset, self.token_external, self.external_network.coin],
            mint_status=True
        )