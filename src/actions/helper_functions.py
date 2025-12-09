from src.utils.data_structures import AgentInfo

def max_lots_available(agents : list[AgentInfo]):
    if not agents:
        return 0
    return max(agent.max_lots for agent in agents)

def can_mint(balances, token_underlying, lot_size, agents):
    enough_collateral = token_underlying in balances and balances[token_underlying] >= lot_size
    available_agents = max_lots_available(agents) >= 1
    return enough_collateral and available_agents

def can_enter_pool(balances, token_underlying):
    return token_underlying in balances and balances[token_underlying] > 0