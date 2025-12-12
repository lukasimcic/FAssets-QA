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
    min_amount = CollateralPool.min_nat_to_enter
    return token_native in balances and balances[token_native] >= min_amount

def add_max_amount_to_stay_above_exit_CR(pool_holdings, token_native, token_underlying):
    for pool_holding in pool_holdings:
        cp = CollateralPool(token_native, pool_holding.pool_address)
        pool_holding.max_amount_to_exit = cp.max_amount_to_stay_above_exit_CR(token_underlying)
    return pool_holdings

def collateral_to_tokens(token_native, pool, amount_native):
    cp = CollateralPool(token_native, pool)   
    cpt = CollateralPoolToken(token_native, cp.pool_token())
    collateral = cpt.to_uba(amount_native)
    total_collateral = cp.total_collateral()
    total_pool_tokens = cpt.total_supply()
    if total_collateral == 0 or total_pool_tokens == 0:
        return cpt.from_uba(collateral)
    tokens = (total_pool_tokens * collateral) / total_collateral
    return cpt.from_uba(tokens)

def tokens_to_collateral(token_native, pool, amount_pool_tokens):
    cp = CollateralPool(token_native, pool)   
    cpt = CollateralPoolToken(token_native, cp.pool_token())
    pool_tokens = cpt.to_uba(amount_pool_tokens)
    total_collateral = cp.total_collateral()
    total_pool_tokens = cpt.total_supply()
    collateral = (total_collateral * pool_tokens) / total_pool_tokens
    return cpt.from_uba(collateral)
    
def tokens_to_fees(token_native, pool, amount_pool_tokens):
    cp = CollateralPool(token_native, pool)   
    cpt = CollateralPoolToken(token_native, cp.pool_token())
    pool_tokens = cpt.to_uba(amount_pool_tokens)
    total_fees = cp.total_fAsset_fees()
    total_pool_tokens = cpt.total_supply()
    fees = (total_fees * pool_tokens) / total_pool_tokens
    return cpt.from_uba(fees)