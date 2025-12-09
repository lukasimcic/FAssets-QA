from src.utils.fee_tracker import FeeTracker
from config.config_qa import tokens_native, tokens_underlying, fasset_name
from dataclasses import dataclass, field
from typing import Dict, Literal, Optional, Union
import math

# TODO maybe class TokenNative(Enum): C2FLR = "C2FLR" ...
# Allowed tokens are also defined in config: tokens_native, tokens_underlying, fasset_name
TokenNative = Literal["C2FLR"]
TokenUnderlying = Literal["testXRP"]
TokenFasset = Literal["FTestXRP"]
Token = Union[TokenNative, TokenUnderlying, TokenFasset]

@dataclass
class UserData:
    token_native: TokenNative
    token_underlying: TokenUnderlying
    num: int
    partner: bool = False
    def partner_data(self):
        return UserData(
            token_native=self.token_native,
            token_underlying=self.token_underlying,
            num=self.num,
            partner=not self.partner
        )
    
@dataclass
class UserUnderlyingData:
    address: str
    private_key: str
    public_key: str

@dataclass
class UserNativeData:
    address: str
    private_key: str

@dataclass
class Balances:
    data: Dict[Token, float] = field(default_factory=dict)
    compare_tolerance = 1e-12
    def __getitem__(self, key):
        return self.data[key]
    def __setitem__(self, key, value):
        self.data[key] = value
    def __contains__(self, key):
        return key in self.data
    def copy(self):
        return Balances(data=self.data.copy())
    def __eq__(self, other):
        if not isinstance(other, Balances):
            return False
        if self.data.keys() != other.data.keys():
            return False
        for k in self.data:
            v1 = self.data[k]
            v2 = other.data[k]
            if not math.isclose(v1, v2, rel_tol=0, abs_tol=self.compare_tolerance):
                return False
        return True
    def __repr__(self):
        items = []
        for k, v in self.data.items():
            if isinstance(v, float):
                items.append(f"{k}: {v:.12f}")
            else:
                items.append(f"{k}: {v}")
        return f"Balances({{{', '.join(items)}}})"
    def subtract_fees(self, fee_tracker : FeeTracker):
        for token in self.data:
            if token in tokens_native:
                self.data[token] -= fee_tracker.native_fees()
            elif token in tokens_underlying:
                self.data[token] -= fee_tracker.underlying_fees()

@dataclass
class MintStatus:
    pending: list = field(default_factory=list)
    expired: list = field(default_factory=list)
    def copy(self):
        return MintStatus(
            pending=self.pending.copy(),
            expired=self.expired.copy()
        )
    def get_all_ids(self):
        return self.pending + self.expired
    def __eq__(self, other):
        if not isinstance(other, MintStatus):
            return False
        for field in self.__dataclass_fields__:
            l1 = getattr(self, field)
            l2 = getattr(other, field)
            if sorted(l1) != sorted(l2):
                return False
        return True

@dataclass
class RedemptionStatus:
    pending: list = field(default_factory=list)
    success: list = field(default_factory=list)
    default: list = field(default_factory=list)
    expired: list = field(default_factory=list)
    def copy(self):
        return RedemptionStatus(
            pending=self.pending.copy(),
            success=self.success.copy(),
            default=self.default.copy(),
            expired=self.expired.copy()
        )
    def get_all_ids(self):
        return self.pending + self.success + self.default + self.expired
    def __eq__(self, other):
        if not isinstance(other, RedemptionStatus):
            return False
        for field in self.__dataclass_fields__:
            l1 = getattr(self, field)
            l2 = getattr(other, field)
            if sorted(l1) != sorted(l2):
                return False
        return True

@dataclass
class Pool:
    address: str
    token_symbol: Optional[str] = None
    token_price_native: Optional[float] = None
    collateral_native: Optional[float] = None
    fees_underlying: Optional[float] = None
    cr: Optional[float] = None
    def __repr__(self):
        return repr_none_filtered(self)

@dataclass
class PoolHolding:
    pool_address: str
    pool_tokens: float
    token_symbol: Optional[str] = None
    compare_tolerance = 1e-12
    def __repr__(self):
        return repr_none_filtered(self)
    def __eq__(self, other):
        if not isinstance(other, PoolHolding):
            return False
        for field in self.__dataclass_fields__:
            v1 = getattr(self, field)
            v2 = getattr(other, field)
            if type(v1) is float:
                if not math.isclose(v1, v2, rel_tol=0, abs_tol=self.compare_tolerance):
                    return False
            else:
                if v1 != v2:
                    return False
        return True

@dataclass
class FlowState:
    balances: Balances
    mint_status: MintStatus
    redemption_status: RedemptionStatus
    pools: list[Pool]
    pool_holdings: list[PoolHolding]
    def __post_init__(self):
        self.pools = sorted(self.pools, key=lambda p: p.address)
        self.pool_holdings = sorted(self.pool_holdings, key=lambda ph: ph.pool_address)
    def replace(self, changes : list):
        for change in changes:
            if type(change) is Balances:
                self.balances = change
            elif type(change) is MintStatus:
                self.mint_status = change
            elif type(change) is RedemptionStatus:
                self.redemption_status = change
            elif type(change) is list and len(change) > 0:
                if type(change[0]) is Pool:
                    self.pools = change
                elif type(change[0]) is PoolHolding:
                    self.pool_holdings = change
        return self
    def fields(self):
        return self.__dataclass_fields__.keys()
    def __getitem__(self, key):
        return getattr(self, key)
    def copy(self):
        return FlowState(
            balances=self.balances.copy(),
            mint_status=self.mint_status.copy(),
            redemption_status=self.redemption_status.copy(),
            pools=self.pools.copy(),
            pool_holdings=self.pool_holdings.copy()
        )
    
@dataclass
class AgentInfo:
    address: str
    max_lots: int
    fee: int # in BIPS


# helper functions

def repr_none_filtered(obj):
    field_strs = [
        f"{k}={repr(v)}"
        for k, v in obj.__dict__.items()
        if v is not None
    ]
    return f"{obj.__class__.__name__}({', '.join(field_strs)})"