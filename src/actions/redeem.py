import random
from src.utils.data_storage import DataStorageClient
from src.interfaces.contracts.asset_manager import AssetManager
from src.actions.action_bundle import ActionBundle
from src.utils.data_structures import FlowState


class RedeemRandomAmount(ActionBundle):
    def __init__(self, user_data, flow_state, cli):
        super().__init__(user_data, flow_state, cli)

    def condition(self) -> bool:
        if self.token_fasset in self.balances: 
            return self.balances[self.token_fasset] >= self.lot_size
        return False

    def action(self) -> None:
        # action logic
        possible_lots = int(self.balances[self.token_fasset] // self.lot_size)
        lot_amount = random.randint(1, possible_lots)
        remaining_lots = self.ca.redeem(lot_amount, log_steps=True)
        # data for expected_state
        self.lot_amount = lot_amount
        self.remaining_lots = remaining_lots

    @property
    def expected_state(self) -> FlowState:
        # balances
        new_balances = self.balances.copy()
        new_balances[self.token_fasset] -= self.lot_size * (self.lot_amount - self.remaining_lots)
        new_balances.subtract_fees(self.ca.fee_tracker)
        # redemption status
        new_redemption_status = self.redemption_status.copy()
        dsc = DataStorageClient(self.user_data, "redeem")
        redemption_ids = dsc.get_new_record_ids(previous_ids=new_redemption_status.get_all_ids())
        new_redemption_status.pending.extend(redemption_ids)
        return self.flow_state.replace([new_balances, new_redemption_status])


class RedeemDefaultRandomRedemption(ActionBundle):
    def __init__(self, user_data, flow_state, cli):
        super().__init__(user_data, flow_state, cli)

    def condition(self) -> bool:
        return self.redemption_status.default

    def action(self) -> None:
        # action logic
        redemption_id = random.choice(self.redemption_status.default)
        # data for expected_state
        dsc = DataStorageClient(self.user_data, "redeem")
        self.record = dsc.get_record(redemption_id)
        self.redemption_id = redemption_id
        # action logic continued
        self.ca.redeem_default(redemption_id, log_steps=True)

    @property
    def expected_state(self) -> FlowState:
        # balances
        lot_amount = self.record["lots"]
        redemption_fee = AssetManager(self.token_native, self.token_underlying).redemption_fee()
        new_balances = self.balances.copy()
        new_balances[self.token_underlying] += self.lot_size * lot_amount * (1 - redemption_fee)
        new_balances.subtract_fees(self.ca.fee_tracker)
        # redemption status
        new_redemption_status = self.redemption_status.copy()
        new_redemption_status.default.remove(self.redemption_id)
        return self.flow_state.replace([new_balances, new_redemption_status])