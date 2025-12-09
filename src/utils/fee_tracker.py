class FeeTracker:
    def __init__(self):
        self.native_gas_fees = 0
        self.native_other_fees = 0
        self.underlying_gas_fees = 0
        self.underlying_other_fees = 0

    def native_fees(self):
        """
        Return total accumulated native fees (gas + other).
        Reset fee counters after retrieval.
        """
        fees = self.native_gas_fees + self.native_other_fees
        self.native_gas_fees = 0
        self.native_other_fees = 0
        return fees

    def underlying_fees(self):
        """
        Return total accumulated underlying fees (gas + other).
        Reset fee counters after retrieval.
        """
        fees = self.underlying_gas_fees + self.underlying_other_fees
        self.underlying_gas_fees = 0
        self.underlying_other_fees = 0
        return fees