from pprint import pprint
import random
import time
from typing import TYPE_CHECKING
from src.actions.action_bundle import ActionBundle
from src.interfaces.network.tokens import TokenExternalFAsset, TokenExternalNative, TokenNative
from src.utils.data_structures import RelevantInfo
if TYPE_CHECKING:
    from src.utils.data_structures import FlowState
    from src.utils.data_structures import UserData

BRIDGE_FEE = {
    TokenNative.C2FLR: 50,
    TokenExternalNative.HYPE_HyperEVM_testnet: 0.1,
}

def to_builtin(obj):
    """Recursively convert custom objects (AttributeDict, HexBytes, etc.) to built-in types."""
    if isinstance(obj, dict):
        return {to_builtin(k): to_builtin(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_builtin(i) for i in obj]
    elif hasattr(obj, 'hex'):  # for HexBytes
        return obj.hex()
    elif hasattr(obj, '__dict__'):  # for AttributeDict
        return to_builtin(vars(obj))
    else:
        return obj

class _BridgeToExternalNetwork(ActionBundle):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool, token_external: "TokenExternalFAsset"):
        super().__init__(user_data, flow_state, cli)
        self.token_external = token_external
        self.external_network = token_external.network

    def condition(self) -> bool:
        enough_fasset = self.balances[self.token_fasset] >= self.lot_size
        enough_fees = self.balances[self.token_native] >= BRIDGE_FEE[self.token_native]
        return enough_fasset and enough_fees
    
    def action(self) -> None:
        # action logic
        max_lots = min(int(self.balances[self.token_fasset] // self.lot_size), 5)
        lot_amount = random.randint(1, max_lots)
        self.ca.bridge_to(self.external_network, lot_amount, log_steps=True)
        # wait for bridge to be processed so that state can be correctly tracked
        time.sleep(60 * 5)
        # data for expected_state
        self.lot_amount = lot_amount

    @property
    def expected_state(self) -> "FlowState":
        new_balances = self.balances.copy()
        new_balances[self.token_fasset] -= self.lot_size * self.lot_amount
        new_balances[self.token_external] += self.lot_size * self.lot_amount
        new_balances.subtract_fees(self.ca.fee_tracker)
        return self.flow_state.replace([new_balances])
    
    def relevant_info(self) -> "RelevantInfo":
        return RelevantInfo(
            tokens=[self.token_native, self.token_fasset, self.token_external, self.external_network.coin]
        )
    

class _BridgeFromExternalNetwork(ActionBundle):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool, token_external: "TokenExternalFAsset"):
        super().__init__(user_data, flow_state, cli)
        self.token_external = token_external
        self.external_network = token_external.network

    def condition(self) -> bool:
        enough_external = self.balances[self.token_external] >= self.lot_size
        enough_fees = self.balances[self.external_network.coin] >= BRIDGE_FEE[self.external_network.coin]
        return enough_external and enough_fees
    
    def action(self) -> None:
        # action logic
        max_lots = min(int(self.balances[self.token_external] // self.lot_size), 5)
        lot_amount = random.randint(1, max_lots)
        self.ca.bridge_from(self.external_network, lot_amount, log_steps=True)
        # wait for bridge to be processed so that state can be correctly tracked
        time.sleep(60 * 5)
        # data for expected_state
        self.lot_amount = lot_amount

    @property
    def expected_state(self) -> "FlowState":
        new_balances = self.balances.copy()
        new_balances[self.token_fasset] += self.lot_size * self.lot_amount
        new_balances[self.token_external] -= self.lot_size * self.lot_amount
        new_balances.subtract_fees(self.ca.fee_tracker)
        return self.flow_state.replace([new_balances])
    
    def relevant_info(self) -> "RelevantInfo":
        return RelevantInfo(
            tokens=[self.token_native, self.token_fasset, self.token_external, self.external_network.coin]
        )


class _AutoRedeemFromExternalNetwork(ActionBundle):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool, token_external: "TokenExternalFAsset"):
        super().__init__(user_data, flow_state, cli)
        self.token_external = token_external
        self.external_network = token_external.network

    def condition(self) -> bool:
        enough_external = self.balances[self.token_external] >= self.lot_size
        enough_fees = self.balances[self.external_network.coin] >= BRIDGE_FEE[self.external_network.coin]
        return enough_external and enough_fees
    
    def action(self) -> None:
        # action logic
        max_lots = min(int(self.balances[self.token_external] // self.lot_size), 5)
        lot_amount = random.randint(1, max_lots)
        x = self.ca.auto_redeem_from(self.external_network, lot_amount, log_steps=True)
        pprint(to_builtin(x))
        # wait for bridge to be processed so that state can be correctly tracked
        time.sleep(60 * 5) 
        # data for expected_state
        self.lot_amount = lot_amount

    @property
    def expected_state(self) -> "FlowState":
        new_balances = self.balances.copy()
        new_balances[self.token_underlying] += self.lot_size * self.lot_amount
        new_balances[self.token_external] -= self.lot_size * self.lot_amount
        new_balances.subtract_fees(self.ca.fee_tracker)
        return self.flow_state.replace([new_balances])
    
    def relevant_info(self) -> "RelevantInfo":
        return RelevantInfo(
            tokens=[self.token_underlying, self.token_native, self.token_fasset, self.token_external, self.external_network.coin]
        )


class BridgeToHyperEVM(_BridgeToExternalNetwork):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool):
        super().__init__(user_data, flow_state, cli, TokenExternalFAsset.FTestXRP_HyperEVM_testnet)


class BridgeToHyperCore(_BridgeToExternalNetwork):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool):
        super().__init__(user_data, flow_state, cli, TokenExternalFAsset.FTestXRP_HyperCore_testnet)


class BridgeFromHyperEVM(_BridgeFromExternalNetwork):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool):
        super().__init__(user_data, flow_state, cli, TokenExternalFAsset.FTestXRP_HyperEVM_testnet)


class AutoRedeemFromHyperEVM(_AutoRedeemFromExternalNetwork):
    def __init__(self, user_data: "UserData", flow_state: "FlowState", cli: bool):
        super().__init__(user_data, flow_state, cli, TokenExternalFAsset.FTestXRP_HyperEVM_testnet)