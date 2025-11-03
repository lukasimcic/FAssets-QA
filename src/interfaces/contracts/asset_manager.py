from .contract_client import ContractClient
from src.utils.contracts import get_contract_address, get_output_index
from config.config_qa import asset_manager_path, asset_manager_testxrp_instance_name, zero_address

class AssetManager(ContractClient):
    def __init__(self, sender_address, sender_private_key, token_underlying):
        match token_underlying:
            case "testXRP": 
                asset_manager_instance_name = asset_manager_testxrp_instance_name
            case _:
                raise ValueError(f"Unsupported underlying token: {token_underlying}")
        asset_manager_address =  get_contract_address(asset_manager_instance_name)
        super().__init__(sender_address, sender_private_key, asset_manager_path, asset_manager_address)

    # info

    def _agent_info(self, agent_vault):
        agent_info = self.read("getAgentInfo", inputs=[agent_vault])
        return agent_info

    def get_available_agents_detailed_list(asset_manager, start, end):
        agent_list = asset_manager.read(
            "getAvailableAgentsDetailedList",
            inputs=[start, end]
        )[0]
        idxs = {}
        fields = ["agentVault", "freeCollateralLots", "feeBIPS"]
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

    def collateral_pool_token_timelock_seconds(self):
        settings = self.read("getSettings")
        idx = get_output_index(self.path, "getSettings", "collateralPoolTokenTimelockSeconds")
        return settings[idx]
    
    def lot_size(self):
        settings = self.read("getSettings")
        idx = get_output_index(self.path, "getSettings", "lotSizeAMG")
        lot_size_anm = settings[idx]
        lot_size = lot_size_anm // self.asset_unit_uba()
        return lot_size

    def asset_unit_uba(self):
        settings = self.read("getSettings")
        idx = get_output_index(self.path, "getSettings", "assetUnitUBA")
        return settings[idx]

    # mint
    
    def _agent_fee_BIPS(self, agent_vault):
        agent_info = self._agent_info(agent_vault)
        idx = get_output_index(self.path, "getAgentInfo", "feeBIPS")
        return agent_info[idx]
    
    def _collateral_reservation_fee(self, lots):
        fee = self.read("collateralReservationFee", inputs=[lots])
        return fee
    
    def reserve_collateral(self, agentVault, lots, executor=zero_address):
        agent_fee_BIPS = self._agent_fee_BIPS(agentVault)
        collateral_reservation_fee = self._collateral_reservation_fee(lots)
        collateralReserved = self.write(
            "reserveCollateral",
            inputs=[agentVault, lots, agent_fee_BIPS, executor],
            events=["CollateralReserved"],
            value=collateral_reservation_fee
        )
        return collateralReserved["CollateralReserved"][0]

    def execute_minting(self, proof, collateral_reservation_id):
        """
        Execute minting after receiving attestation proof.
        """
        _, receipt = self.write(
            "executeMinting",
            inputs=[proof, collateral_reservation_id],
            return_receipt=True
        )
        return receipt
    
    # redeem

    def redeem(self, lots, underlying_address, executor, executor_fee):
        """
        Redeem given lots. Returns requested redemption data.
        """
        events = self.write(
            "redeem",
            inputs=[lots, underlying_address, executor],
            events=["RedemptionRequested", "RedemptionRequestIncomplete"],
            value=executor_fee,
        )
        return events["RedemptionRequested"], events["RedemptionRequestIncomplete"]

    def redemption_request_info(self, redemption_request_id):
        """
        Get redemption request info by id.
        """
        redemption_info = self.read(
            "redemptionRequestInfo",
            inputs=[redemption_request_id]
        )
        return redemption_info

    def redemption_queue(self, first_redemption_ticket_id=0, page_size=10):
        """
        Get redemption queue starting from given ticket id.
        """
        queue = self.read(
            "redemptionQueue",
            inputs=[first_redemption_ticket_id, page_size]
        )
        return queue
    
    def redemption_payment_default(self, proof, redemption_request_id):
        """
        Execute redemption payment default after receiving attestation proof.
        """
        _, receipt = self.write(
            "redemptionPaymentDefault",
            inputs=[proof, redemption_request_id],
            return_receipt=True
        )
        return receipt