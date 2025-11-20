from src.interfaces.contracts.asset_manager import AssetManager


def get_agents(self, chunk_size=10):
    agent_list = []
    start = 0
    am = AssetManager("", "", self.minter.token_underlying)
    while True:
        new = am.get_available_agents_detailed_list(start, start + chunk_size)
        agent_list.extend(new)
        if len(new) < chunk_size:
            break
        start += len(new)
    fields_mapping = {
        "agentVault": "address",
        "freeCollateralLots": "max_lots",
        "feeBIPS": "fee"
        }
    result = []
    for agent in agent_list:
        d = {}
        for k, v in agent.items():
            if k == "feeBIPS":
                d[fields_mapping[k]] = v / 100  # convert to percentage
            else:
                d[fields_mapping[k]] = v
        result.append(d)
    return result

def max_lots(agents):
    if not agents:
        return 0
    return max(agent["max_lots"] for agent in agents)

def can_mint(balances, token_underlying, lot_size, agents):
    enough_collateral = token_underlying in balances and balances[token_underlying] >= lot_size
    available_agents = max_lots(agents) >= 1
    return enough_collateral and available_agents