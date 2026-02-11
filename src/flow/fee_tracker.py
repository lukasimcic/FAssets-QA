from decimal import Decimal
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from src.interfaces.network.tokens import Coin


class FeeTracker:
    def __init__(self):
        self.gas_fees = {}
        self.other_fees = {}

    def update_fees(
            self, 
            token: "Coin", 
            gas_fees: Optional[Decimal] = None, 
            other_fees: Optional[Decimal] = None
            ):
        if gas_fees is not None:
            if token not in self.gas_fees:
                self.gas_fees[token] = Decimal(0)
            self.gas_fees[token] += gas_fees
        if other_fees is not None:
            if token not in self.other_fees:
                self.other_fees[token] = Decimal(0)
            self.other_fees[token] += other_fees

    def get_fees(self, token: "Coin") -> Decimal:
        """
        Return total accumulated fees (gas + other) for the given token.
        Reset fee counters after retrieval.
        """
        fees = Decimal(0)
        fees += self.gas_fees.pop(token, Decimal(0))
        fees += self.other_fees.pop(token, Decimal(0))
        return fees