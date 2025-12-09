import traceback
from src.actions.action_bundle import ActionBundle
from src.actions.core_actions.core_actions_cli import CoreActionsCLI
from src.actions.core_actions.core_actions_manual import CoreActionsManual
from src.actions import ACTION_BUNDLE_CLASSES
from src.utils.data_structures import UserData, FlowState
import random
import time

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
        user_data: UserData,
        actions,
        cli=False,
        total_time=None, 
        time_wait=60
    ):
        self.user_data = user_data
        self.partner_data = user_data.partner_data()
        self.actions = actions
        self.cli = cli
        self.total_time = total_time
        self.time_wait = time_wait

        # core actions for logging and state retrieval
        if cli:
            self.ca = CoreActionsCLI(user_data)
            self.ca_partner = CoreActionsCLI(self.partner_data)
        else:
            self.ca = CoreActionsManual(user_data)
            self.ca_partner = CoreActionsManual(self.partner_data)

    def log(self, message, both=True):
        self.ca.log(message)
        if both:
            self.ca_partner.log(message)

    def update_flow_state(self, log_steps=True):
        self.flow_state = FlowState(
            self.ca.get_balances(log_steps=log_steps),
            self.ca.get_mint_status(log_steps=log_steps),
            self.ca.get_redemption_status(log_steps=log_steps),
            [], # self.ca.get_pools(log_steps=log_steps),
            [], # self.ca.get_pool_holdings(log_steps=log_steps)
        )
    
    def _step(self):
        self.update_flow_state()

        action_bundles = []
        for cls in ACTION_BUNDLE_CLASSES:
            if cls.__name__ in self.actions:
                bundle = cls(
                        self.user_data,
                        self.flow_state,
                        self.cli
                    )
                if bundle.condition():
                    action_bundles.append(bundle)
        
        if action_bundles:
            bundle : ActionBundle = random.choice(action_bundles)
            self.log(f"-- Executing action {bundle.__class__.__name__} --", both=False)
            
            successful = True
            try:
                bundle.action()
            except Exception as e:
                self.log(f"Action failed with exception: {e}\n{traceback.format_exc()}")
                successful = False
            
            if successful:
                self.update_flow_state(log_steps=False)
                state_mismatches = {}
                for field in self.flow_state.fields():
                    actual_value = self.flow_state[field]
                    expected_value = bundle.expected_state[field]
                    if actual_value != expected_value:
                        state_mismatches[field] = (expected_value, actual_value)
                if not state_mismatches:
                    self.log("Action successfully executed.")
                else:
                    successful = False
                    mismatch_str = "\n".join(
                        f"{field.capitalize()}:\n    expected: {expected}\n    actual:   {actual}"
                        for field, (expected, actual) in state_mismatches.items()
                    )
                    self.log(
                        f"State mismatch after action execution!\n{mismatch_str}"
                    )
            return successful

    def run(self):
        self.log(f"----- Starting flow. -----")
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
                    self.log("--- Total time reached, stopping flow. ---")
                    self.log(f"----- Flow finished. Successful steps: {successful_steps}/{all_steps} -----")
                    break
                else:
                    self.log(f"--- Step finished, time left: {self.total_time:.2f} seconds. ---")