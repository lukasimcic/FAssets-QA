import random
from src.actions.action_bundle import ActionBundle
from src.actions.helper_functions import can_mint, max_lots_available
from src.utils.data_storage import DataStorageClient
from src.utils.data_structures import FlowState


class MintLowestFeeAgentRandomAmount(ActionBundle):
    def __init__(self, user_data, flow_state, cli):
        super().__init__(user_data, flow_state, cli)
        self.agents_dict = self.ca.get_agents()

    def condition(self) -> bool:
        return can_mint(self.balances, self.token_underlying, self.lot_size, self.agents_dict)
    
    def action(self) -> None:
        # action logic
        agent_fees_dict = {
            agent_fee: [
                agent for agent in self.agents_dict if agent.fee == agent_fee and agent.max_lots >= 1
                ] 
                for agent_fee in set(agent.fee for agent in self.agents_dict)
            }
        lowest_fee = min(fee for fee, agents in agent_fees_dict.items() if agents)
        agents = agent_fees_dict[lowest_fee]
        agent = random.choice(agents)
        possible_lots = int(self.balances[self.token_underlying] // self.lot_size)
        max_lots = min(agent.max_lots, possible_lots)
        lot_amount = random.randint(1, max_lots)
        self.ca.mint(lot_amount, agent=agent.address, log_steps=True)
        # data for expected_state
        self.lot_amount = lot_amount
        self.agent = agent

    @property
    def expected_state(self) -> FlowState:
        new_balances = self.balances.copy()
        new_balances[self.token_underlying] -= self.lot_size * self.lot_amount * (1 + self.agent.fee)
        new_balances[self.token_fasset] += self.lot_size * self.lot_amount
        new_balances.subtract_fees(self.ca.fee_tracker)
        return self.flow_state.replace([new_balances])


class MintRandomAgentRandomAmount(ActionBundle):
    def __init__(self, user_data, flow_state, cli):
        super().__init__(user_data, flow_state, cli)
    
    def condition(self) -> bool:
        self.agents_dict = self.ca.get_agents()
        return can_mint(self.balances, self.token_underlying, self.lot_size, self.agents_dict)
    
    def action(self) -> None:
        # action logic
        agents = [agent for agent in self.agents_dict if agent.max_lots >= 1]
        agent = random.choice(agents)
        possible_lots = int(self.balances[self.token_underlying] // self.lot_size)
        max_lots = min(agent.max_lots, possible_lots)
        lot_amount = random.randint(1, max_lots)
        self.ca.mint(lot_amount, agent=agent.address, log_steps=True)
        # data for expected_state
        self.lot_amount = lot_amount
        self.agent = agent

    @property
    def expected_state(self) -> FlowState:
        new_balances = self.balances.copy()
        new_balances[self.token_underlying] -= self.lot_size * self.lot_amount * (1 + self.agent.fee)
        new_balances[self.token_fasset] += self.lot_size * self.lot_amount
        new_balances.subtract_fees(self.ca.fee_tracker)
        return self.flow_state.replace([new_balances])


class MintExecuteRandomMinting(ActionBundle):
    def __init__(self, user_data, flow_state, cli):
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
    def expected_state(self) -> FlowState:
        # balances
        new_balances = self.balances.copy()
        new_balances[self.token_fasset] += self.lot_size * self.record["lots"]
        new_balances.subtract_fees(self.ca.fee_tracker)
        # mint status
        new_mint_status = self.mint_status.copy()
        new_mint_status.pending.remove(self.mint_id)
        return self.flow_state.replace([new_balances, new_mint_status])


class MintRandomAgentRandomAmountBlockUnderlying(MintRandomAgentRandomAmount):
    def __init__(self, user_data, flow_state, cli):
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