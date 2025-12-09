from src.interfaces.contracts.collateral_pool import CollateralPool
from src.interfaces.contracts.collateral_pool_token import CollateralPoolToken
from src.utils.data_structures import AgentInfo

def max_lots_available(agents : list[AgentInfo]):
    if not agents:
        return 0
    return max(agent.max_lots for agent in agents)

def can_mint(balances, token_underlying, lot_size, agents):
    enough_collateral = token_underlying in balances and balances[token_underlying] >= lot_size
    available_agents = max_lots_available(agents) >= 1
    return enough_collateral and available_agents

def can_enter_pool(balances, token_native):
    return token_native in balances and balances[token_native] >= 1

def collateral_to_token_share(pool, amount_native):
    cp = CollateralPool(pool)   
    cpt = CollateralPoolToken(cp.pool_token())
    factor = 10 ** cpt.decimals()
    collateral = int(amount_native * factor)
    total_collateral = cp.total_collateral()
    total_pool_tokens = cpt.total_supply()
    if total_collateral == 0 or total_pool_tokens == 0:
        return collateral / factor
    return (total_pool_tokens * collateral / total_collateral) / factor