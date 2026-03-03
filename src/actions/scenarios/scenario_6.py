from typing import TYPE_CHECKING
from src.actions.scenarios.base_scenarios import ScenarioMintBridgeBridgeRedeem
from src.interfaces.network.tokens import TokenExternalFAsset
if TYPE_CHECKING:
    from src.utils.data_structures import UserData
    from src.utils.data_structures import FlowState


class Scenario6(ScenarioMintBridgeBridgeRedeem):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool):
        super().__init__(user_data, flow_state, cli, TokenExternalFAsset.FTestXRP_HyperEVM_testnet)