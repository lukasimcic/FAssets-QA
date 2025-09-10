from src.utils.config import token_fasset, token_underlying, lot_size

class FlowConditions:
    def __init__(self, flow):
        self.flow = flow

    def can_mint(self):
        if token_underlying in self.flow.balances:
            return self.flow.balances[token_underlying] >= lot_size
        return False

    def can_mint_random(self):
        return self.can_mint()

    def can_redeem(self):
        if token_fasset in self.flow.balances: 
            return self.flow.balances[token_fasset] >= lot_size
        return False

    def can_mint_execute(self):
        return self.flow.mint_status["PENDING"]

    def can_redeem_default(self):
        return self.flow.redemption_status["DEFAULT"]

    def can_enter_pool(self):
        if token_underlying in self.flow.balances:
            if self.flow.balances[token_underlying] > 0:
                return self.flow.pools
        return False

    def can_exit_pool(self):
        return self.flow.pool_holdings

    def can_withdraw_pool_fees(self):
        return self.flow.pool_holdings

    def can_scenario_1(self):
        pass  # TODO