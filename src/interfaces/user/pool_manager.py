from src.interfaces.user.user import User
from src.interfaces.contracts import *
from src.interfaces.network.native_networks.native_network import NativeNetwork
from src.interfaces.network.underlying_networks.underlying_network import UnderlyingNetwork
from src.interfaces.network.attestation import Attestation
from src.utils.data_storage_client import DataStorageClient


class PoolManager(User):
    def __init__(self, token_native, token_underlying, num=0, partner=False, config=None):
        super().__init__(token_native, token_underlying, num, partner)
        self.native_address = self.native_data["address"]
        self.native_private_key = self.native_data["private_key"]
        self.underlying_public_key = self.underlying_data["public_key"]
        self.underlying_private_key = self.underlying_data["private_key"]
        # TODO add support for custom config
        if config is not None:
            raise NotImplementedError("Custom config is not yet supported.")
        
    def enter_pool(self, pool, amount, log_steps=False):
        """
        Enter the collateral pool by calling the CollateralPool contract.
        Amount is in pool tokens, not in UBA.
        """
        cp = CollateralPool(self.native_address, self.native_private_key, pool)
        cpt = CollateralPoolToken("", "", cp.pool_token())
        amount_UBA = int(amount * 10 ** cpt.decimals())
        cp.enter(amount_UBA)

    def exit_pool(self, pool, amount, log_steps=False):
        """
        Exit the collateral pool by calling the CollateralPool contract.
        Amount is in pool tokens, not in UBA.
        """
        cp = CollateralPool(self.native_address, self.native_private_key, pool)
        cpt = CollateralPoolToken("", "", cp.pool_token())
        amount_UBA = int(amount * 10 ** cpt.decimals())
        cp.exit(amount_UBA)

    def withdraw_pool_fees(self, pool, fees, log_steps=False):
        """
        Withdraw fees from the collateral pool by calling the CollateralPool contract.
        """
        cp = CollateralPool(self.native_address, self.native_private_key, pool)
        cp.withdraw_fees(fees)

    def pools(self, chunk_size=10, log_steps=False):
        """
        Get dictionary of collateral pools and their details.
        """
        agent_list = []
        start = 0
        am = AssetManager("", "", self.token_underlying)
        while True:
            new = am.get_available_agents_detailed_list(start, start + chunk_size)
            agent_list.extend(new)
            if len(new) < chunk_size:
                break
            start += len(new)
        result = []
        for agent in agent_list:
            agent_dict = {"Pool address": am.agent_attribute(agent["agentVault"], "collateralPool")}
            # add more details as needed
            result.append(agent_dict)
        return result
    
    def pool_holdings(self, log_steps=False):
        """
        Get the holdings of the specified collateral pool.
        """
        result = []
        all_pools = self.pools(log_steps=log_steps)
        for pool in all_pools:
            pool_address = pool["Pool address"]
            cp = CollateralPool("", "", pool_address)
            debt_free_tokens = cp.debt_free_tokens_of(self.native_address)
            debt_locked_tokens = cp.debt_locked_tokens_of(self.native_address)
            tokens = debt_free_tokens + debt_locked_tokens
            if tokens > 0:
                cpt = CollateralPoolToken("", "", cp.pool_token())
                tokens = tokens / 10 ** cpt.decimals()
                pool_dict = {"Pool address": pool_address, "Pool tokens": tokens}
                result.append(pool_dict)
        return result
    
    def pool_fees(self, log_steps=False):
        """
        Get the fees available to withdraw from collateral pools.
        """
        result = []
        all_pools = self.pools(log_steps=log_steps)
        for pool in all_pools:
            pool_address = pool["Pool address"]
            cp = CollateralPool("", "", pool_address)
            fees = cp.fAsset_fees_of(self.native_address)
            if fees > 0:
                cpt = CollateralPoolToken("", "", cp.pool_token())
                fees = fees / 10 ** cpt.decimals()
                pool_dict = {"Pool address": pool_address, "Pool fees": fees}
                result.append(pool_dict)
        return result

    # TODO implement in flow
    def max_amount_to_stay_above_exit_CR(self, pool, log_steps=False):
        """
        Check if the pool stays above the exit CR after exiting with amount.
        """
        am = AssetManager("", "", self.token_underlying)
        cp = CollateralPool("", "", pool)
        cpt = CollateralPoolToken("", "", cp.pool_token())
        asset_price = am.asset_price_nat_wei()
        backed_fAssets = am.get_fAssets_backed_by_pool(cp.agent_vault())
        exit_cr = cp.exit_collateral_ratio_bips() / 1e4
        # from (N - n) q >= F p cr
        amount_UBA = cp.total_collateral() - backed_fAssets * exit_cr * asset_price["mul"] / asset_price["div"]
        return amount_UBA / (10 ** cpt.decimals())