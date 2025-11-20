from src.flow.flow_actions.action_bundle import ActionBundle
import random

class RedeemRandomAmount(ActionBundle):
    def __init__(self, ca, ca_partner, user, partner, lot_size, state):
        super().__init__(ca, ca_partner, user, partner, lot_size, state)

    def action(self):
        lot_amount = random.randint(1, self.balances[self.token_fasset] // self.lot_size)
        self.ca.redeem(lot_amount, log_steps=True)

    def condition(self):
        if self.token_fasset in self.balances: 
            return self.balances[self.token_fasset] >= self.lot_size
        return False

    def state_after(self):
        raise NotImplementedError("State update is not implemented yet.")


class RedeemDefaultRandomRedemption(ActionBundle):
    def __init__(self, ca, ca_partner, user, partner, lot_size, state):
        super().__init__(ca, ca_partner, user, partner, lot_size, state)

    def action(self):
        redemption_id = random.choice(self.redemption_status["DEFAULT"])
        self.ca.redeem_default(redemption_id, log_steps=True)

    def condition(self):
        return self.redemption_status["DEFAULT"]

    def state_after(self):
        raise NotImplementedError("State update is not implemented yet.")
