from decimal import Decimal
import random
from typing import TYPE_CHECKING
from src.interfaces.contracts.collateral_pool import CollateralPool
from src.interfaces.contracts.collateral_pool_token import CollateralPoolToken
if TYPE_CHECKING:
    from src.interfaces.network.tokens import TokenFAsset, TokenNative, TokenUnderlying
    from src.interfaces.network.networks.native_networks.native_network import NativeNetwork
    from src.utils.data_structures import AgentInfo, PoolHolding


def max_lots_available(agents : list["AgentInfo"]) -> int:
    if not agents:
        return 0
    return max(agent.max_lots for agent in agents)

def can_mint(balances, token_underlying: "TokenUnderlying", lot_size: int, agents: list["AgentInfo"]) -> bool:
    enough_collateral = token_underlying in balances and balances[token_underlying] >= lot_size
    available_agents = max_lots_available(agents) >= 1
    return enough_collateral and available_agents

def can_enter_pool(balances, token_native: "TokenNative") -> bool:
    min_amount = CollateralPool.min_nat_to_enter
    return token_native in balances and balances[token_native] >= min_amount

def add_max_amount_to_stay_above_exit_CR(pool_holdings: list["PoolHolding"], native_network: "NativeNetwork", token_fasset: "TokenFAsset") -> list["PoolHolding"]:
    for pool_holding in pool_holdings:
        cp = CollateralPool(native_network, pool_holding.pool_address)
        pool_holding.max_amount_to_exit = cp.max_amount_to_stay_above_exit_CR(token_fasset)
    return pool_holdings

def collateral_to_tokens(native_network: "NativeNetwork", pool: str, amount_native: Decimal) -> Decimal:
    cp = CollateralPool(native_network, pool)   
    cpt = CollateralPoolToken(native_network, cp.pool_token())
    collateral = cpt.to_uba(amount_native)
    total_collateral = cp.total_collateral()
    total_pool_tokens = cpt.total_supply()
    if total_collateral == 0 or total_pool_tokens == 0:
        return cpt.from_uba(collateral)
    tokens = (total_pool_tokens * collateral) / total_collateral
    return cpt.from_uba(tokens)

def tokens_to_collateral(native_network: "NativeNetwork", pool: str, amount_pool_tokens: Decimal) -> Decimal:
    cp = CollateralPool(native_network, pool)   
    cpt = CollateralPoolToken(native_network, cp.pool_token())
    pool_tokens = cpt.to_uba(amount_pool_tokens)
    total_collateral = cp.total_collateral()
    total_pool_tokens = cpt.total_supply()
    collateral = (total_collateral * pool_tokens) / total_pool_tokens
    return cpt.from_uba(collateral)
    
def tokens_to_fees(native_network: "NativeNetwork", pool: str, amount_pool_tokens: Decimal) -> Decimal:
    cp = CollateralPool(native_network, pool)   
    cpt = CollateralPoolToken(native_network, cp.pool_token())
    pool_tokens = cpt.to_uba(amount_pool_tokens)
    total_fees = cp.total_fAsset_fees()
    total_pool_tokens = cpt.total_supply()
    fees = (total_fees * pool_tokens) / total_pool_tokens
    return cpt.from_uba(fees)

def random_decimal_between(a: Decimal, b: Decimal) -> Decimal:
    r = Decimal(str(random.random()))
    return a + (b - a) * r