from decimal import Decimal
from typing import Optional
from src.interfaces.network.tokens import TokenNative, TokenUnderlying
from src.interfaces.user.state_manager import StateManager
from src.interfaces.user.user import User
from src.interfaces.contracts import *
from src.utils.data_structures import UserData
from src.utils.secrets import get_user_nums


class Funder(User):
    def __init__(self, token_native: TokenNative, token_underlying: TokenUnderlying, user_nums: Optional[list[int]]  = None):
        self.user_data = UserData(
            token_native=token_native,
            token_underlying=token_underlying,
            funder=True
        )
        super().__init__(self.user_data)
        if user_nums:
            self.user_nums = user_nums
        else:
            self.user_nums = get_user_nums()
        self.funder_reserve = Decimal(len(self.user_nums) + 1)
        self.user_reserve = Decimal(1)

    def request_funds(self) -> None:
        nn = self.token_native.network(self.native_credentials)
        un = self.token_underlying.network(self.underlying_credentials)
        try:
            value = nn.request_funds()
            self.logger.info(f"Requested {value} {self.token_native.name} funds.")
        except Exception as e:
            self.logger.info(f"Error requesting native funds: {e}")
        try:
            value = un.request_funds()
            self.logger.info(f"Requested {value} {self.token_underlying.name} funds.")
        except Exception as e:
            self.logger.info(f"Error requesting underlying funds: {e}")

    def _send_native_funds_to_user(self, num: int, amount: Decimal) -> None:
        amount_uba = self.token_native.to_uba(amount)
        nn = self.token_native.network(self.native_credentials)
        user_data = UserData(
            token_native=self.token_native,
            token_underlying=self.token_underlying,
            num=num
        )
        sm = StateManager(user_data)
        nn.send_transaction(sm.native_credentials.address, amount_uba)

    def _send_underlying_funds_to_user(self, num: int, amount: Decimal) -> None:
        un = self.token_underlying.network(self.underlying_credentials)
        user_data = UserData(
            token_native=self.token_native,
            token_underlying=self.token_underlying,
            num=num
        )
        sm = StateManager(user_data)
        un.send_transaction(sm.underlying_credentials.address, amount)

    def _check_reserves(self) -> None:
        """
        Check if all users and partner users have at least reserve amount of both native and underlying tokens.
        If not, send funds to those users to bring them up to the reserve.
        """
        for num in self.user_nums:
            for partner in [False, True]:
                user_sm = StateManager(
                    UserData(
                        token_native=self.token_native,
                        token_underlying=self.token_underlying,
                        num=num,
                        partner=partner
                    )
                )
                balances = user_sm.get_balances()
                native_balance = balances.get(self.token_native)
                if native_balance < self.user_reserve:
                    amount_to_send = self.user_reserve - native_balance
                    self._send_native_funds_to_user(num, amount_to_send)
                    self.logger.info(f"Sent {amount_to_send} {self.token_native.name} to {'partner ' if partner else ''}user {num} to meet reserve.")
                underlying_balance = balances.get(self.token_underlying)
                if underlying_balance < self.user_reserve:
                    amount_to_send = self.user_reserve - underlying_balance
                    self._send_underlying_funds_to_user(num, amount_to_send)
                    self.logger.info(f"Sent {amount_to_send} {self.token_underlying.name} to {'partner ' if partner else ''}user {num} to meet reserve.")

    def distribute_funds(self, max_to_send : Decimal = Decimal(300)) -> None:
        self._check_reserves()
        sm = StateManager(self.user_data)
        balances = sm.get_balances()
        self.logger.info(f"Funder balances before fund distribution: {balances}.")
        native_to_send = (balances.get(self.token_native) - self.funder_reserve) / len(self.user_nums)
        native_to_send = min(native_to_send, max_to_send)
        underlying_to_send = (balances.get(self.token_underlying) - self.funder_reserve) / len(self.user_nums)
        underlying_to_send = min(underlying_to_send, max_to_send)
        for num in self.user_nums:
            if native_to_send > 0:
                self._send_native_funds_to_user(num, native_to_send)
                self.logger.info(f"Sent {native_to_send} {self.token_native.name} to user {num}.")
            if underlying_to_send > 0:
                self._send_underlying_funds_to_user(num, underlying_to_send)
                self.logger.info(f"Sent {underlying_to_send} {self.token_underlying.name} to user {num}.")

    def collect_funds(self) -> None:
        for num in self.user_nums:
            user_sm = StateManager(
                UserData(
                    token_native=self.token_native,
                    token_underlying=self.token_underlying,
                    num=num
                )
            )
            balances = user_sm.get_balances()
            self.logger.info(f"User {num} balances before collection: {balances}.")
            native_to_send = balances.get(self.token_native) - self.user_reserve * Decimal(1.01)
            if native_to_send > 0:
                native_to_send_uba = self.token_native.to_uba(native_to_send)
                nn = self.token_native.network(user_sm.native_credentials)
                nn.send_transaction(self.native_credentials.address, native_to_send_uba)
                self.logger.info(f"Collected {native_to_send} {self.token_native.name} from user {num}.")
            underlying_to_send = balances.get(self.token_underlying) - self.user_reserve * Decimal(1.01)
            if underlying_to_send > 0:
                un = self.token_underlying.network(user_sm.underlying_credentials)
                un.send_transaction(self.underlying_credentials.address, underlying_to_send)
                self.logger.info(f"Collected {underlying_to_send} {self.token_underlying.name} from user {num}.")