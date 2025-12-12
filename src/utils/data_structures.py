from enum import Enum
from src.utils.fee_tracker import FeeTracker
from config.config_qa import contracts_file_coston2, asset_manager_instance_name_testxrp, fasset_instance_name_testxrp, fdc_url, da_url, rpc_url
from dataclasses import dataclass, field
from typing import Dict, Optional, Union
import math

# TODO C2FLR -> coston2
class TokenNative(Enum):
    C2FLR = ("C2FLR", contracts_file_coston2, 18)
    def __init__(self, name, contracts_file, decimals):
        self._name_ = name
        self.contracts_file = contracts_file
        self.decimals = decimals
        self.compare_tolerance = 10 ** (-decimals + 3)
        self.rpc_url = rpc_url[name]
        self.fdc_url = fdc_url[name]
        self.da_url = da_url[name]
    def to_uba(self, amount: float) -> int:
        return int(amount * 10 ** self.decimals)
    def from_uba(self, amount_uba: int) -> float:
        return amount_uba / 10 ** self.decimals

class TokenUnderlying(Enum):
    testXRP = ("testXRP", asset_manager_instance_name_testxrp, fasset_instance_name_testxrp, 6)
    def __init__(self, name, asset_manager_instance_name, fasset_instance_name, decimals):
        self._name_ = name
        self.asset_manager_instance_name = asset_manager_instance_name
        self.fasset_instance_name = fasset_instance_name
        self.decimals = decimals
        self.compare_tolerance = 10 ** (-decimals + 1)
        self.rpc_url = rpc_url[name]
    def to_uba(self, amount: float) -> int:
        return int(amount * 10 ** self.decimals)
    def from_uba(self, amount_uba: int) -> float:
        return amount_uba / 10 ** self.decimals

class TokenFasset(Enum):
    testXRP_fasset = ("FTestXRP", TokenUnderlying.testXRP)
    def __init__(self, name, token_underlying : TokenUnderlying):
        self._name_ = name
        self.token_underlying = token_underlying
        self.decimals = token_underlying.decimals
        self.compare_tolerance = 10 ** -self.decimals
    @classmethod
    def from_underlying(cls, underlying: TokenUnderlying):
        name = f"{underlying.name}_fasset"
        return cls[name]
    def to_uba(self, amount: float) -> int:
        return int(amount * 10 ** self.decimals)
    def from_uba(self, amount_uba: int) -> float:
        return amount_uba / 10 ** self.decimals
    
Token = Union[TokenNative, TokenUnderlying, TokenFasset]

@dataclass
class UserData:
    token_native: TokenNative
    token_underlying: TokenUnderlying
    num: int
    partner: bool = False
    def __post_init__(self):
        if not isinstance(self.token_native, TokenNative):
            self.token_native = TokenNative(self.token_native)
        if not isinstance(self.token_underlying, TokenUnderlying):
            self.token_underlying = TokenUnderlying(self.token_underlying)
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
            if not math.isclose(v1, v2, rel_tol=0, abs_tol=k.compare_tolerance):
                return False
        return True
    def __repr__(self):
        items = []
        for k, v in self.data.items():
            if isinstance(v, float):
                items.append(f"{k.name}: {v:.12f}")
            else:
                items.append(f"{k.name}: {v}")
        return f"Balances({{{', '.join(items)}}})"
    def subtract_fees(self, fee_tracker : FeeTracker):
        for token in self.data:
            if isinstance(token, TokenNative):
                self.data[token] -= fee_tracker.native_fees()
            elif isinstance(token, TokenUnderlying):
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
        return _repr_none_filtered(self)

@dataclass
class PoolHolding:
    pool_address: str
    pool_tokens: float = 0
    fasset_fees: float = 0
    token_symbol: Optional[str] = None
    max_amount_to_exit: Optional[float] = None
    def __repr__(self):
        return _repr_none_filtered(self)
    def __eq__(self, other):
        if not isinstance(other, PoolHolding):
            return False
        for field in self.__dataclass_fields__:
            v1 = getattr(self, field)
            v2 = getattr(other, field)
            if type(v1) is float:
                if field == "pool_tokens":
                    compare_tolerance = 1e-15 # TODO de-hardcode
                elif field == "fasset_fees":
                    compare_tolerance = 1e-8 # TODO de-hardcode
                if not math.isclose(v1, v2, rel_tol=0, abs_tol=compare_tolerance):
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
    pool_holdings: list[PoolHolding]
    def __post_init__(self):
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
            pool_holdings=self.pool_holdings.copy()
        )
    
@dataclass
class AgentInfo:
    address: str
    max_lots: int
    fee: int # in BIPS


# helper functions

def _repr_none_filtered(obj):
    field_strs = [
        f"{k}={repr(v)}"
        for k, v in obj.__dict__.items()
        if v is not None
    ]
    return f"{obj.__class__.__name__}({', '.join(field_strs)})"