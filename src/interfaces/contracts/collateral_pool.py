from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from src.utils.contracts import get_contract_names
from .contract_client import ContractClient
from src.interfaces.contracts.asset_manager import AssetManager
from src.interfaces.contracts.collateral_pool_token import CollateralPoolToken
if TYPE_CHECKING:
    from src.interfaces.network.networks.native_networks.native_network import NativeNetwork
    from src.interfaces.network.tokens import TokenFAsset
    from src.utils.data_structures import UserCredentials
    from src.flow.fee_tracker import FeeTracker


class CollateralPool(ContractClient):
    min_nat_to_enter = Decimal(1)
    def __init__(
            self, 
            network: "NativeNetwork",
            pool_address: str, 
            sender_credentials: Optional["UserCredentials"]  = None, 
            fee_tracker: Optional["FeeTracker"]  = None
        ):
        names = get_contract_names(self)
        super().__init__(names, network, pool_address, sender_credentials=sender_credentials, fee_tracker=fee_tracker)

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
    
    def max_amount_to_stay_above_exit_CR(self, token_fasset: "TokenFAsset") -> Decimal:
        """
        Returns the maximum amount of collateral that can be exited from the pool.
        """
        am = AssetManager(self.network, token_fasset)
        cpt = CollateralPoolToken(self.network, self.pool_token())
        asset_price = am.asset_price_nat_wei()
        backed_fAssets = am.get_fAssets_backed_by_pool(self.agent_vault())
        exit_cr = self.exit_collateral_ratio_bips() / 1e4
        # from (N - n) q >= F p cr
        amount_UBA = self.total_collateral() - backed_fAssets * exit_cr * asset_price["mul"] / asset_price["div"]
        amount = cpt.from_uba(amount_UBA)
        return max(amount, Decimal(0))
