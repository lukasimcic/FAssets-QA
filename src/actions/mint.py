from src.actions.action_bundle import ActionBundle
import random


def can_mint(balances, token_underlying, lot_size):
    return token_underlying in balances and balances[token_underlying] >= lot_size


class MintLowestFeeAgentRandomAmount(ActionBundle):
    def __init__(self, ca, ca_partner, user, partner, lot_size, state):
        super().__init__(ca, ca_partner, user, partner, lot_size, state)
    
    def action(self):
        lot_amount = random.randint(1, self.balances[self.token_underlying] // self.lot_size + 1)
        agents = []
        current_lowest_fee = None
        for agent in self.ca.get_agents():
            if agent["max_lots"] * self.lot_size >= lot_amount:
                if current_lowest_fee is None or agent["fee"] < current_lowest_fee:
                    agents = [agent["address"]]
                    current_lowest_fee = agent["fee"]
                elif agent["fee"] == current_lowest_fee:
                    agents.append(agent["address"])
        agent = random.choice(agents)
        self.ca.mint(lot_amount, agent=agent, log_steps=True)

    def condition(self):
        return can_mint(self.balances, self.token_underlying, self.lot_size)

    def state_after(self):
        raise NotImplementedError("State update is not implemented yet.")


class MintRandomAgentRandomAmount(ActionBundle):
    def __init__(self, ca, ca_partner, user, partner, lot_size, state):
        super().__init__(ca, ca_partner, user, partner, lot_size, state)
    
    def action(self):
        lot_amount = random.randint(1, self.balances[self.token_underlying] // self.lot_size + 1)
        agents = []
        for agent in self.ca.get_agents():
            if agent["max_lots"] * self.lot_size >= lot_amount:
                agents.append(agent["address"])
        agent = random.choice(agents)
        self.ca.mint(lot_amount, agent=agent, log_steps=True)

    def condition(self):
        return can_mint(self.balances, self.token_underlying, self.lot_size)

    def state_after(self):
        raise NotImplementedError("State update is not implemented yet.")


class MintExecuteRandomMinting(ActionBundle):
    def __init__(self, ca, ca_partner, user, partner, lot_size, state):
        super().__init__(ca, ca_partner, user, partner, lot_size, state)

    def action(self):
        mint_id = random.choice(self.mint_status["PENDING"])
        self.ca.mint_execute(mint_id)

    def condition(self):
        return self.mint_status["PENDING"]

    def state_after(self):
        raise NotImplementedError("State update is not implemented yet.")
