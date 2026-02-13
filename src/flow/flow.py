import traceback
import random
import time
from typing import TYPE_CHECKING, Literal, Optional
from src.actions.core_actions.core_actions import core_actions
from src.actions import ACTION_BUNDLE_CLASSES
from src.utils.data_structures import RelevantInfo, FlowState
if TYPE_CHECKING:
    from src.actions.action_bundle import ActionBundle
    from src.actions.core_actions.core_actions import CoreActions
    from src.utils.data_structures import UserData


class Flow():
    """
    This is the base class for flow implementations.
    In a flow, user actions are repeatedly chosen at random among a set of possible actions, if their conditions are met.
    
    Flow classes hierarchy:
    - Flow (this class)
        - ActionBundles
            - contracts (just for general network info)
            - CoreActions
                - contracts (just for general network info)
                - users (e.g., Minter, Redeemer, UserBot, ...)
                    - UnderlyingNetworks
                    - contracts
                        - NativeNetworks
                    - Attestation
                        - contracts
    """
    def __init__(
        self,
        user_data: "UserData",
        actions: list[str],
        cli: bool = False,
        total_time: Optional[int]  = None, 
        time_wait: int = 60
    ):
        self.user_data = user_data
        self.partner_data = user_data.partner_data()
        self.actions = actions
        self.cli = cli
        self.total_time = total_time
        self.time_wait = time_wait

        # core actions for logging and state retrieval
        self.ca = core_actions(user_data, cli)
        self.ca_partner = core_actions(self.partner_data, cli)
        self.relevant_info = RelevantInfo.union([
            ab(self.user_data, FlowState.new(), self.cli).relevant_info()
            for ab in ACTION_BUNDLE_CLASSES if ab.__name__ in actions
            ])

    def _log(
            self, 
            message: str, level: Literal["info", "warning", "error"], 
            partner: bool = False
        ) -> None:
        self.ca.log(message, level)
        if partner:
            self.ca_partner.log(message, level)

    @staticmethod
    def _flow_state(ca: "CoreActions", relevant_info: "RelevantInfo", log_steps: bool) -> "FlowState":
        flow_state = FlowState(ca.get_balances(relevant_info.tokens, log_steps))
        if relevant_info.mint_status:
            flow_state.mint_status = ca.get_mint_status(log_steps)
        if relevant_info.redemption_status:
            flow_state.redemption_status = ca.get_redemption_status(log_steps)
        if relevant_info.pool_holdings:
            flow_state.pool_holdings = ca.get_pool_holdings(log_steps)
        return flow_state

    def _update_flow_state(self, log_steps: bool = True) -> None:
        self.flow_state = self._flow_state(self.ca, self.relevant_info, log_steps)

    def _get_partner_flow_state(self, log_steps: bool = True) -> "FlowState":
        return self._flow_state(self.ca_partner, self.relevant_info, log_steps)
    
    def _step(self) -> Optional[bool] :
        self._update_flow_state()

        action_bundles = []
        for cls in ACTION_BUNDLE_CLASSES:
            if cls.__name__ in self.actions:
                bundle = cls(
                        self.user_data,
                        self.flow_state,
                        self.cli
                    )
                if bundle.general_conditions() and bundle.condition():
                    action_bundles.append(bundle)
        
        if not action_bundles:
            self._log("-- No action can be executed at this time. --", level="info")
            return None

        else:
            bundle : "ActionBundle" = random.choice(action_bundles)
            self._log(f"-- Executing action {bundle.__class__.__name__} --", level="info")
            
            successful = True
            if bundle.partner_involved:
                partner_flow_state = self._get_partner_flow_state()
                bundle.update_partner_flow_state(partner_flow_state)
            try:
                bundle.action()
            except Exception as e:
                self._log(
                    f"Action {bundle.__class__.__name__} failed with exception: {e}\n{traceback.format_exc()}",
                    level="error"
                )
                successful = False
            
            if successful:
                expected_state = bundle.expected_state
                self._update_flow_state(log_steps=False)
                state_mismatches = self.flow_state.compare(expected_state)
                if bundle.partner_involved:
                    partner_flow_state = self._get_partner_flow_state(log_steps=False)
                    partner_expected_state = bundle.partner_expected_state
                    partner_state_mismatches = partner_flow_state.compare(partner_expected_state)
                else:
                    partner_state_mismatches = [{}]
                if min(len(m) for m in state_mismatches) == min(len(m) for m in partner_state_mismatches) == 0:
                    self._log("Action successfully executed.", level="info")
                else:
                    successful = False
                    for user, state_mismatches in zip(["", "Partner "], [state_mismatches, partner_state_mismatches]):
                        for state_mismatche in state_mismatches:
                            if state_mismatche:
                                mismatch_str = "\n".join(
                                    f"{user}{field.capitalize()}:\n    expected: {expected}\n    actual:   {actual}"
                                    for field, (actual, expected) in state_mismatche.items()
                                )
                                self._log(
                                    f"State mismatch after action execution!\n{mismatch_str}", level="warning"
                                )
            return successful

    def run(self) -> None:
        self._log(f"----- Starting flow. -----", level="info", partner=True)
        all_actions = len(ACTION_BUNDLE_CLASSES) == len(self.actions)
        if all_actions:
            self._log("----- All actions available. -----", level="info")
        else:
            self._log(f"----- Available actions: {', '.join(self.actions)}. -----", level="info")
        successful_steps = 0
        all_steps = 0
        t = time.time()
        while True:
            successful = self._step()
            time.sleep(self.time_wait)
            if successful:
                successful_steps += 1
            if successful is not None:
                all_steps += 1
            if self.total_time:
                self.total_time -= time.time() - t
                if self.total_time <= 0:
                    self._log("--- Total time reached, stopping flow. ---", level="info", partner=True)
                    self._log(f"----- Flow finished. Successful steps: {successful_steps}/{all_steps} -----", level="info")
                    break
                else:
                    self._log(f"--- Step finished, time left: {self.total_time:.2f} seconds. ---", level="info")