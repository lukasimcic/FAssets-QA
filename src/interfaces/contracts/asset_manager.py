from typing import Any

from src.utils.data_structures import TokenNative, TokenUnderlying, UserNativeData
from src.flow.fee_tracker import FeeTracker
from .contract_client import ContractClient
from src.utils.contracts import get_contract_address, get_output_index
from config.config_qa import asset_manager_path, zero_address


class AssetManager(ContractClient):
    def __init__(
            self, 
            token_native: TokenNative,
            token_underlying: TokenUnderlying, 
            sender_data: UserNativeData | None = None, 
            fee_tracker: FeeTracker | None = None
        ):
        self.token_native = token_native
        self.token_underlying = token_underlying
        asset_manager_address =  get_contract_address(
            token_underlying.asset_manager_instance_name, 
            token_native
            )
        super().__init__(token_native, asset_manager_path, asset_manager_address, sender_data, fee_tracker)

    # info

    def agent_attribute(self, agent_vault: str, attribute: str) -> Any:
        agent_info = self.read("getAgentInfo", inputs=[agent_vault])
        idx = get_output_index(self.path, "getAgentInfo", attribute)
        return agent_info[idx]

    def get_available_agents_detailed_list(self, start: int, end: int) -> list[dict[str, Any]]:
        agent_list = self.read(
            "getAvailableAgentsDetailedList",
            inputs=[start, end]
        )[0]
        idxs = {}
        fields = [
            "agentVault", 
            "freeCollateralLots", 
            "feeBIPS", 
            "mintingPoolCollateralRatioBIPS",
            "mintingVaultCollateralRatioBIPS"
        ]
        for field in fields:
            idxs[field] = get_output_index(
                asset_manager_path,
                "getAvailableAgentsDetailedList",
                field
            )
        result = []
        for agent in agent_list:
            agent_info = {field: agent[idxs[field]] for field in fields}
            result.append(agent_info)
        return result

    def collateral_pool_token_timelock_seconds(self) -> int:
        settings = self.read("getSettings")
        idx = get_output_index(self.path, "getSettings", "collateralPoolTokenTimelockSeconds")
        return settings[idx]
    
    def lot_size(self) -> float:
        settings = self.read("getSettings")
        idx = get_output_index(self.path, "getSettings", "lotSizeAMG")
        lot_size_uba = settings[idx]
        return self.token_underlying.from_uba(lot_size_uba)

    def asset_price_nat_wei(self) -> dict[str, int]:
        asset_price_mul, asset_price_div = self.read("assetPriceNatWei")
        return {
            "mul": asset_price_mul,
            "div": asset_price_div
        }
    
    def redemption_fee_bips(self) -> int:
        settings = self.read("getSettings")
        idx = get_output_index(self.path, "getSettings", "redemptionFeeBIPS")
        fee_bips = settings[idx]
        return fee_bips

    def max_redeemed_tickets(self) -> int:
        settings = self.read("getSettings")
        idx = get_output_index(self.path, "getSettings", "maxRedeemedTickets")
        max_tickets = settings[idx]
        return max_tickets

    def get_fAssets_backed_by_pool(self, vault_address: str) -> int:
        return self.read(
            "getFAssetsBackedByPool",
            inputs=[vault_address]
        )

    # mint
    
    def collateral_reservation_fee(self, lots: int) -> int:
        fee = self.read("collateralReservationFee", inputs=[lots])
        return fee
    
    def reserve_collateral(self, agentVault: str, lots: int, executor: str = zero_address) -> dict:
        agent_fee_BIPS = self.agent_attribute(agentVault, "feeBIPS")
        collateral_reservation_fee = self.collateral_reservation_fee(lots)
        collateralReserved = self.write(
            "reserveCollateral",
            inputs=[agentVault, lots, agent_fee_BIPS, executor],
            events=["CollateralReserved"],
            value=collateral_reservation_fee
        )["events"]
        self.fee_tracker.native_other_fees += self.token_native.from_uba(collateral_reservation_fee)
        return collateralReserved["CollateralReserved"][0]

    def execute_minting(self, proof: tuple, collateral_reservation_id: int) -> dict:
        """
        Execute minting after receiving attestation proof.
        """
        receipt = self.write(
            "executeMinting",
            inputs=[proof, collateral_reservation_id]
        )["receipt"]
        return receipt
    
    # redeem

    def redeem(self, lots: int, underlying_address: str, executor: str, executor_fee: int) -> dict:
        """
        Redeem given lots. Returns RedemptionRequested and RedemptionRequestIncomplete events.
        """
        events = self.write(
            "redeem",
            inputs=[lots, underlying_address, executor],
            events=["RedemptionRequested", "RedemptionRequestIncomplete"],
            value=executor_fee
        )["events"]
        return events

    def redemption_request_info(self, redemption_request_id: int) -> tuple:
        """
        Get redemption request info by id.
        """
        redemption_info = self.read(
            "redemptionRequestInfo",
            inputs=[redemption_request_id]
        )
        return redemption_info

    def redemption_queue(self, first_redemption_ticket_id: int = 0, page_size: int = 10) -> list:
        """
        Get redemption queue starting from given ticket id.
        """
        queue = self.read(
            "redemptionQueue",
            inputs=[first_redemption_ticket_id, page_size]
        )
        return queue
    
    def redemption_payment_default(self, proof: tuple, redemption_request_id: int) -> dict:
        """
        Execute redemption payment default after receiving attestation proof.
        """
        receipt = self.write(
            "redemptionPaymentDefault",
            inputs=[proof, redemption_request_id]
        )["receipt"]
        return receipt