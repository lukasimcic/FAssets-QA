from decimal import Decimal
from src.interfaces.contracts.collateral_pool_token import CollateralPoolToken
from src.interfaces.contracts.asset_manager import AssetManager
from src.utils.data_structures import TokenNative, UserNativeData
from src.flow.fee_tracker import FeeTracker
from .contract_client import ContractClient
from config.config_qa import collateral_pool_path


class CollateralPool(ContractClient):
    min_nat_to_enter = Decimal(1)
    def __init__(
            self, 
            token_native: TokenNative,
            pool_address: str, 
            sender_data: UserNativeData | None = None, 
            fee_tracker: FeeTracker | None = None
        ):
        super().__init__(token_native, collateral_pool_path, pool_address, sender_data, fee_tracker)

    def agent_vault(self) -> str:
        return self.read("agentVault")
    
    def pool_token(self) -> str:
        return self.read("poolToken")

    def debt_free_tokens_of(self, address: str) -> int:
        return self.read("debtFreeTokensOf", [address])
    
    def debt_locked_tokens_of(self, address: str) -> int:
        return self.read("debtLockedTokensOf", [address])

    def enter(self, amount: int) -> dict:
        return self.write("enter", value=amount)["events"]
    
    def exit(self, amount: int) -> dict:
        return self.write("exit", [amount])["events"]

    def withdraw_fees(self, fees: int) -> dict:
        return self.write("withdrawFees", [fees])["events"]
    
    def total_collateral(self) -> int:
        return self.read("totalCollateral")
    
    def exit_collateral_ratio_bips(self) -> int:
        return self.read("exitCollateralRatioBIPS")
    
    def total_fAsset_fees(self) -> int:
        return self.read("totalFAssetFees")

    def fAsset_fees_of(self, address: str) -> int:
        return self.read("fAssetFeesOf", [address])
    
    def max_amount_to_stay_above_exit_CR(self, token_underlying) -> Decimal:
        """
        Returns the maximum amount of collateral that can be exited from the pool.
        """
        am = AssetManager(self.token_native, token_underlying)
        cpt = CollateralPoolToken(self.token_native, self.pool_token())
        asset_price = am.asset_price_nat_wei()
        backed_fAssets = am.get_fAssets_backed_by_pool(self.agent_vault())
        exit_cr = self.exit_collateral_ratio_bips() / 1e4
        # from (N - n) q >= F p cr
        amount_UBA = self.total_collateral() - backed_fAssets * exit_cr * asset_price["mul"] / asset_price["div"]
        amount = cpt.from_uba(amount_UBA)
        return max(amount, Decimal(0)) 
