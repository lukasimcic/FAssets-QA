from src.interfaces.user.user import User
from src.interfaces.contracts import *
from src.utils.data_structures import Pool, PoolHolding, UserData
from src.utils.fee_tracker import FeeTracker


class PoolManager(User):
    def __init__(self, user_data : UserData, fee_tracker : FeeTracker | None = None):
        super().__init__(user_data, fee_tracker)
        self.native_address = self.native_data.address
        
    def enter_pool(self, pool, amount, log_steps=False):
        """
        Enter the collateral pool by calling the CollateralPool contract.
        Amount is in pool tokens, not in UBA.
        """
        cp = CollateralPool(pool, self.native_data, self.fee_tracker)
        cpt = CollateralPoolToken(cp.pool_token())
        amount_UBA = int(amount * 10 ** cpt.decimals())
        cp.enter(amount_UBA)

    def exit_pool(self, pool, amount, log_steps=False):
        """
        Exit the collateral pool by calling the CollateralPool contract.
        Amount is in pool tokens, not in UBA.
        """
        cp = CollateralPool(pool, self.native_data, self.fee_tracker)
        cpt = CollateralPoolToken(cp.pool_token())
        amount_UBA = int(amount * 10 ** cpt.decimals())
        cp.exit(amount_UBA)

    def withdraw_pool_fees(self, pool, fees, log_steps=False):
        """
        Withdraw fees from the collateral pool by calling the CollateralPool contract.
        """
        cp = CollateralPool(pool, self.native_data, self.fee_tracker)
        cp.withdraw_fees(fees)

    def pools(self, chunk_size=10, log_steps=False):
        """
        Get dictionary of collateral pools and their details.
        """
        agent_list = []
        start = 0
        am = AssetManager(self.token_underlying)
        while True:
            new = am.get_available_agents_detailed_list(start, start + chunk_size)
            agent_list.extend(new)
            if len(new) < chunk_size:
                break
            start += len(new)
        result = []
        for agent in agent_list:
            pool_dict = {"address": am.agent_attribute(agent["agentVault"], "collateralPool")}
            # add more details as needed
            result.append(Pool(**pool_dict))
        return result
    
    def pool_holdings(self, log_steps=False):
        """
        Get the user's holdings of all pools.
        """
        result = []
        all_pools = self.pools(log_steps=log_steps)
        for pool in all_pools:
            pool_address = pool.address
            cp = CollateralPool(pool_address)
            debt_free_tokens = cp.debt_free_tokens_of(self.native_address)
            debt_locked_tokens = cp.debt_locked_tokens_of(self.native_address)
            tokens = debt_free_tokens + debt_locked_tokens
            if tokens > 0:
                cpt = CollateralPoolToken(cp.pool_token())
                tokens = tokens / 10 ** cpt.decimals()
                pool_dict = {"pool_address": pool_address, "pool_tokens": tokens}
                result.append(PoolHolding(**pool_dict))
        return result
    
    def pool_fees(self, log_steps=False):
        """
        Get the fees available to withdraw from collateral pools.
        """
        result = []
        all_pools = self.pools(log_steps=log_steps)
        for pool in all_pools:
            pool_address = pool.address
            cp = CollateralPool(pool_address)
            fees = cp.fAsset_fees_of(self.native_address)
            if fees > 0:
                cpt = CollateralPoolToken(cp.pool_token())
                fees = fees / 10 ** cpt.decimals()
                pool_dict = {"Pool address": pool_address, "Pool fees": fees}
                result.append(pool_dict)
        return result

    # TODO implement in flow
    def max_amount_to_stay_above_exit_CR(self, pool, log_steps=False):
        """
        Check if the pool stays above the exit CR after exiting with amount.
        """
        am = AssetManager(self.token_underlying)
        cp = CollateralPool(pool)
        cpt = CollateralPoolToken(cp.pool_token())
        asset_price = am.asset_price_nat_wei()
        backed_fAssets = am.get_fAssets_backed_by_pool(cp.agent_vault())
        exit_cr = cp.exit_collateral_ratio_bips() / 1e4
        # from (N - n) q >= F p cr
        amount_UBA = cp.total_collateral() - backed_fAssets * exit_cr * asset_price["mul"] / asset_price["div"]
        return amount_UBA / (10 ** cpt.decimals())