from src.actions.action_bundle import ActionBundle
from src.actions.helper_functions import can_mint, max_lots_available
from src.utils.data_storage_client import DataStorageClient
import random


class MintLowestFeeAgentRandomAmount(ActionBundle):
    def __init__(self, user_data, flow_state, cli):
        super().__init__(user_data, flow_state, cli)
        self.agents_dict = self.ca.get_agents()

    def condition(self):
        return can_mint(self.balances, self.token_underlying, self.lot_size, self.agents_dict)
    
    def action(self):
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
        max_lots = min(agent.max_lots, self.balances[self.token_underlying] // self.lot_size)
        lot_amount = random.randint(1, max_lots)
        self.ca.mint(lot_amount, agent=agent.address, log_steps=True)
        # data for expected_state
        self.lot_amount = lot_amount
        self.agent = agent

    @property
    def expected_state(self):
        new_balances = self.balances.copy()
        new_balances[self.token_underlying] -= self.lot_size * self.lot_amount * (1 + self.agent.fee / 1e2)
        new_balances[self.token_fasset] += self.lot_size * self.lot_amount
        new_balances.subtract_fees(self.ca.fee_tracker)
        return self.flow_state.replace([new_balances])


class MintRandomAgentRandomAmount(ActionBundle):
    def __init__(self, user_data, flow_state, cli):
        super().__init__(user_data, flow_state, cli)
    
    def condition(self):
        self.agents_dict = self.ca.get_agents()
        return can_mint(self.balances, self.token_underlying, self.lot_size, self.agents_dict)
    
    def action(self):
        # action logic
        agents = [agent for agent in self.agents_dict if agent.max_lots >= 1]
        agent = random.choice(agents)
        max_lots = min(agent.max_lots, self.balances[self.token_underlying] // self.lot_size)
        lot_amount = random.randint(1, max_lots)
        self.ca.mint(lot_amount, agent=agent.address, log_steps=True)
        # data for expected_state
        self.lot_amount = lot_amount
        self.agent = agent

    @property
    def expected_state(self):
        new_balances = self.balances.copy()
        new_balances[self.token_underlying] -= self.lot_size * self.lot_amount * (1 + self.agent.fee / 1e2)
        new_balances[self.token_fasset] += self.lot_size * self.lot_amount
        new_balances.subtract_fees(self.ca.fee_tracker)
        return self.flow_state.replace([new_balances])


class MintExecuteRandomMinting(ActionBundle):
    def __init__(self, user_data, flow_state, cli):
        super().__init__(user_data, flow_state, cli)

    def condition(self):
        return self.mint_status.pending

    def action(self):
        # action logic
        mint_id = random.choice(self.mint_status.pending)
        # data for expected_state
        dsc = DataStorageClient(self.user_data, action_type="mint")
        self.mint_id = mint_id
        self.record = dsc.get_record(mint_id)
        # action logic continued
        self.ca.mint_execute(mint_id, log_steps=True)

    @property
    def expected_state(self):
        # balances
        new_balances = self.balances.copy()
        new_balances[self.token_fasset] += self.lot_size * self.record["lots"]
        new_balances.subtract_fees(self.ca.fee_tracker)
        # mint status
        new_mint_status = self.mint_status.copy()
        new_mint_status.pending.remove(self.mint_id)
        return self.flow_state.replace([new_balances, new_mint_status])

