from decimal import Decimal
from src.interfaces.user.user import User
from src.interfaces.contracts import *
from src.utils.data_structures import Pool, PoolHolding, UserData
from src.flow.fee_tracker import FeeTracker


class PoolManager(User):
    def __init__(self, user_data : UserData, fee_tracker : FeeTracker | None = None):
        super().__init__(user_data, fee_tracker)
        self.native_address = self.native_data.address
        
    def enter_pool(self, pool: str, amount: Decimal, log_steps: bool = False) -> None:
        """
        Enter the collateral pool by calling the CollateralPool contract.
        Amount is in pool tokens (type Decimal), not in UBA (type int).
        """
        cp = CollateralPool(self.token_native, pool, self.native_data, self.fee_tracker)
        cpt = CollateralPoolToken(self.token_native, cp.pool_token())
        amount_UBA = cpt.to_uba(amount)
        cp.enter(amount_UBA)

    def exit_pool(self, pool: str, amount: Decimal, log_steps: bool = False) -> None:
        """
        Exit the collateral pool by calling the CollateralPool contract.
        Amount is in pool tokens (type Decimal), not in UBA (type int).
        """
        cp = CollateralPool(self.token_native, pool, self.native_data, self.fee_tracker)
        cpt = CollateralPoolToken(self.token_native, cp.pool_token())
        amount_UBA = cpt.to_uba(amount)
        cp.exit(amount_UBA)

    def withdraw_pool_fees(self, pool: str, fees: Decimal, log_steps: bool = False) -> None:
        """
        Withdraw fees from the collateral pool by calling the CollateralPool contract.
        Fees is in fasset tokens (type Decimal), not in UBA (type int).
        """
        cp = CollateralPool(self.token_native, pool, self.native_data, self.fee_tracker)
        fees_UBA = self.token_fasset.to_uba(fees)
        cp.withdraw_fees(fees_UBA)

    def pools(self, chunk_size: int = 10, log_steps: bool = False) -> list[Pool]:
        """
        Get dictionary of collateral pools and their details.
        """
        agent_list = []
        start = 0
        am = AssetManager(self.token_native, self.token_underlying)
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
    
    def pool_holdings(self, log_steps: bool = False) -> list[PoolHolding]:
        """
        Get the user's holdings and fasset fees of all pools.
        """
        result = []
        all_pools = self.pools(log_steps=log_steps)
        for pool in all_pools:
            pool_address = pool.address
            pool_dict = {"pool_address": pool_address}
            # holdings
            cp = CollateralPool(self.token_native, pool_address)
            debt_free_tokens = cp.debt_free_tokens_of(self.native_address)
            debt_locked_tokens = cp.debt_locked_tokens_of(self.native_address)
            tokens = debt_free_tokens + debt_locked_tokens
            if tokens > 0:
                cpt = CollateralPoolToken(self.token_native, cp.pool_token())
                tokens = cpt.from_uba(tokens)
                pool_dict["pool_tokens"] = tokens
            # fasset fees
            fees = cp.fAsset_fees_of(self.native_address)
            if fees > 0:
                fees = self.token_fasset.from_uba(fees)
                pool_dict["fasset_fees"] = fees
            if "pool_tokens" in pool_dict or "fasset_fees" in pool_dict:
                result.append(PoolHolding(**pool_dict))
        return result
    
    def transfer_pool_tokens(self, pool_address: str, to_address: str, amount: Decimal, log_steps: bool = False) -> None:
        """
        Transfer pool tokens to another address.
        Amount is in pool tokens (type Decimal), not in UBA (type int).
        """
        cp = CollateralPool(self.token_native, pool_address, self.native_data, self.fee_tracker)
        pool_token_address = cp.pool_token()
        cpt = CollateralPoolToken(self.token_native, pool_token_address, self.native_data, self.fee_tracker)
        amount_UBA = cpt.to_uba(amount)
        cpt.transfer(to_address, amount_UBA)