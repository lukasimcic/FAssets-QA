import random
from typing import TYPE_CHECKING, Optional
from src.actions.core_actions.core_actions import core_actions
from src.actions.action_bundle import ActionBundle
from src.actions.helper_functions import can_mint
from src.utils.data_storage import DataStorageClient
from src.utils.data_structures import RelevantInfo
if TYPE_CHECKING:
    from src.utils.data_structures import FlowState
    from src.utils.data_structures import AgentInfo, UserData


class _MintRandomAmount(ActionBundle):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool, agent_list: Optional[list["AgentInfo"]] = None):
        super().__init__(user_data, flow_state, cli)
        self.agent_list = agent_list if agent_list is not None else self.ca.get_agents()
        available_agents = [agent for agent in self.agent_list if agent.max_lots >= 1]
        self.agent = random.choice(available_agents) if available_agents else None

    def condition(self) -> bool:
        return can_mint(self.balances, self.token_underlying, self.lot_size, self.agent_list)

    def action(self) -> None:
        # action logic
        possible_lots = int(self.balances[self.token_underlying] // self.lot_size)
        max_lots = min(self.agent.max_lots, possible_lots)
        lot_amount = random.randint(1, max_lots)
        self.ca.mint(lot_amount, agent=self.agent.address, log_steps=True)
        # data for expected_state
        self.lot_amount = lot_amount

    @property
    def expected_state(self) -> "FlowState":
        new_balances = self.balances.copy()
        new_balances[self.token_underlying] -= self.lot_size * self.lot_amount * (1 + self.agent.fee)
        new_balances[self.token_fasset] += self.lot_size * self.lot_amount
        new_balances.subtract_fees(self.ca.fee_tracker)
        return self.flow_state.replace([new_balances])

    def relevant_info(self) -> "RelevantInfo":
        return RelevantInfo(
            tokens=[self.token_underlying, self.token_native, self.token_fasset],
            mint_status=True
        )


class MintRandomAgentRandomAmount(_MintRandomAmount):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool):
        super().__init__(user_data, flow_state, cli)


class MintLowestFeeAgentRandomAmount(_MintRandomAmount):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool):
        ca = core_actions(user_data, cli)
        agent_list = ca.get_agents()
        agent_fees_dict = {
            agent_fee: [
                agent for agent in agent_list if agent.fee == agent_fee and agent.max_lots >= 1
                ] 
                for agent_fee in set(agent.fee for agent in agent_list)
            }
        lowest_fee = min(fee for fee, agents in agent_fees_dict.items() if agents)
        self.agent_list = agent_fees_dict[lowest_fee]
        super().__init__(user_data, flow_state, cli, agent_list=self.agent_list)


class MintSpecificAgentRandomAmount(_MintRandomAmount):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool, agent_address: str):
        ca = core_actions(user_data, cli)
        agent_list = ca.get_agents()
        specific_agent = next((agent for agent in agent_list if agent.address == agent_address), None)
        if not specific_agent:
            raise ValueError(f"Agent with address {agent_address} not found.")
        super().__init__(user_data, flow_state, cli, agent_list=[specific_agent])
    

class MintExecuteRandomMinting(ActionBundle):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool):
        super().__init__(user_data, flow_state, cli)

    def condition(self) -> bool:
        return self.mint_status.pending

    def action(self) -> None:
        # action logic
        mint_id = random.choice(self.mint_status.pending)
        # data for expected_state
        dsc = DataStorageClient(self.user_data, action_type="mint")
        self.mint_id = mint_id
        self.record = dsc.get_record(mint_id)
        # action logic continued
        self.ca.mint_execute(mint_id, log_steps=True)

    @property
    def expected_state(self) -> "FlowState":
        # balances
        new_balances = self.balances.copy()
        new_balances[self.token_fasset] += self.lot_size * self.record["lots"]
        new_balances.subtract_fees(self.ca.fee_tracker)
        # mint status
        new_mint_status = self.mint_status.copy()
        new_mint_status.pending.remove(self.mint_id)
        return self.flow_state.replace([new_balances, new_mint_status])

    def relevant_info(self) -> "RelevantInfo":
        return RelevantInfo(
            tokens=[self.token_underlying, self.token_fasset, self.token_native],
            mint_status=True
        )
    

class MintRandomAgentRandomAmountBlockUnderlying(MintRandomAgentRandomAmount):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool):
        if cli:
            raise Exception("MintRandomAgentRandomAmountBlockUnderlying is not available in CLI mode.")
        super().__init__(user_data, flow_state, cli)

    def action(self) -> None:
        sm = self.ca.sm
        sm.block_underlying_deposits()
        try:
            super().action()
        finally:    
            sm.unblock_underlying_deposits()