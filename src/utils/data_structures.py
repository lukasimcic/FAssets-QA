from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Union
from decimal import Decimal
import math

from src.flow.fee_tracker import FeeTracker
from config.config_qa import contracts_file_coston2, asset_manager_instance_name_testxrp, fasset_instance_name_testxrp, fdc_url, da_url, rpc_url, faucet_url


# TODO C2FLR -> coston2
class TokenNative(Enum):
    C2FLR = ("C2FLR", contracts_file_coston2, 18)
    def __init__(self, name: str, contracts_file: Path, decimals: int):
        self._name_ = name
        self.contracts_file = contracts_file
        self.decimals = decimals
        self.compare_tolerance = 10 ** (-decimals + 6)
        self.rpc_url = rpc_url[name]
        self.faucet_url = faucet_url[name]
        self.fdc_url = fdc_url[name]
        self.da_url = da_url[name]

    def to_uba(self, amount: Decimal) -> int:
        return int(amount * 10 ** self.decimals)
    
    def from_uba(self, amount_uba: int) -> Decimal:
        return Decimal(amount_uba) / Decimal(10) ** self.decimals


class TokenUnderlying(Enum):
    testXRP = ("testXRP", asset_manager_instance_name_testxrp, fasset_instance_name_testxrp, 6)
    def __init__(self, name: str, asset_manager_instance_name: str, fasset_instance_name: str, decimals: int):
        self._name_ = name
        self.asset_manager_instance_name = asset_manager_instance_name
        self.fasset_instance_name = fasset_instance_name
        self.decimals = decimals
        self.compare_tolerance = 10 ** (-decimals + 1)
        self.rpc_url = rpc_url[name]
        self.faucet_url = faucet_url[name]

    def to_uba(self, amount: Decimal) -> int:
        return int(amount * 10 ** self.decimals)
    
    def from_uba(self, amount_uba: int) -> Decimal:
        return Decimal(amount_uba) / Decimal(10) ** self.decimals


class TokenFasset(Enum):
    testXRP_fasset = ("FTestXRP", TokenUnderlying.testXRP)
    def __init__(self, name: str, token_underlying: TokenUnderlying):
        self._name_ = name
        self.token_underlying = token_underlying
        self.decimals = token_underlying.decimals
        self.compare_tolerance = 10 ** -self.decimals

    @classmethod
    def from_underlying(cls, underlying: TokenUnderlying):
        name = f"{underlying.name}_fasset"
        return cls[name]
    
    def to_uba(self, amount: Decimal) -> int:
        return int(amount * 10 ** self.decimals)
    
    def from_uba(self, amount_uba: int) -> Decimal:
        return Decimal(amount_uba) / Decimal(10) ** self.decimals
    

Token = Union[TokenNative, TokenUnderlying, TokenFasset]


@dataclass
class UserData:
    token_native: TokenNative
    token_underlying: TokenUnderlying
    num: int | None = None
    partner: bool | None = False
    funder: bool | None = False

    def __post_init__(self):
        if not isinstance(self.token_native, TokenNative):
            self.token_native = TokenNative(self.token_native)
        if not isinstance(self.token_underlying, TokenUnderlying):
            self.token_underlying = TokenUnderlying(self.token_underlying)

    def partner_data(self) -> "UserData":
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
    data: Dict[Token, Decimal] = field(default_factory=dict)

    def __getitem__(self, key: Token) -> Decimal:
        return self.data[key]
    
    def get(self, key: Token, default=None) -> Decimal:
        return self.data.get(key, default)
    
    def __setitem__(self, key: Token, value: Decimal) -> None:
        self.data[key] = value

    def __contains__(self, key: Token) -> bool:
        return key in self.data
    
    def copy(self) -> "Balances":
        return Balances(data=self.data.copy())
    
    def __eq__(self, other: object) -> bool:
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
    
    def __repr__(self) -> str:
        items = []
        for k, v in self.data.items():
            items.append(f"{k.name}: {v:.{int(-math.log10(k.compare_tolerance))}f}")
        return f"Balances({{{', '.join(items)}}})"
    
    def subtract_fees(self, fee_tracker: FeeTracker) -> None:   
        for token in self.data:
            if isinstance(token, TokenNative):
                self.data[token] -= fee_tracker.native_fees()
            elif isinstance(token, TokenUnderlying):
                self.data[token] -= fee_tracker.underlying_fees()


@dataclass
class MintStatus:
    pending: list = field(default_factory=list)
    expired: list = field(default_factory=list)

    def copy(self) -> "MintStatus":
        return MintStatus(
            pending=self.pending.copy(),
            expired=self.expired.copy()
        )
    
    def get_all_ids(self) -> list:
        return self.pending + self.expired
    
    def __eq__(self, other: object) -> bool:
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

    def copy(self) -> "RedemptionStatus":
        return RedemptionStatus(
            pending=self.pending.copy(),
            success=self.success.copy(),
            default=self.default.copy(),
            expired=self.expired.copy()
        )
    
    def get_all_ids(self) -> list:
        return self.pending + self.success + self.default + self.expired
    
    def __eq__(self, other: object) -> bool:
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
    token_price_native: Optional[Decimal] = None
    collateral_native: Optional[Decimal] = None
    fees_underlying: Optional[Decimal] = None
    cr: Optional[float] = None

    def __repr__(self) -> str:
        return _repr_none_filtered(self)


@dataclass
class PoolHolding:
    pool_address: str
    pool_tokens: Decimal = Decimal(0)
    fasset_fees: Decimal = Decimal(0)
    token_symbol: Optional[str] = None
    max_amount_to_exit: Optional[Decimal] = None

    def __repr__(self) -> str:
        obj = self.copy()
        obj.max_amount_to_exit = None
        tolerances = self.compare_tolerances()
        for field in tolerances:
            value = getattr(obj, field)
            setattr(obj, field, f"{value:.{int(-math.log10(tolerances[field]))}f}")
        return _repr_none_filtered(obj)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PoolHolding):
            return False
        for field in self.__dataclass_fields__:
            v1 = getattr(self, field)
            v2 = getattr(other, field)
            if field in ["pool_tokens", "fasset_fees"]:
                tolerance = self.compare_tolerances()[field]
                if not math.isclose(v1, v2, rel_tol=0, abs_tol=tolerance):
                    return False
            elif field not in ["max_amount_to_exit"]:
                if v1 != v2:
                    return False
        return True
    
    def copy(self) -> "PoolHolding":
        return PoolHolding(
            pool_address=self.pool_address,
            pool_tokens=self.pool_tokens,
            fasset_fees=self.fasset_fees,
            token_symbol=self.token_symbol,
            max_amount_to_exit=self.max_amount_to_exit
        )
    
    def compare_tolerances(self) -> dict[str, float]:
        return {
            "pool_tokens": 1e-12, # TODO de-hardcode
            "fasset_fees": 1e-5 # TODO de-hardcode
        }


@dataclass
class FlowState:
    balances: Balances
    mint_status: MintStatus
    redemption_status: RedemptionStatus
    pool_holdings: list[PoolHolding]

    def __post_init__(self):
        self.pool_holdings = sorted(self.pool_holdings, key=lambda ph: ph.pool_address)

    def replace(self, changes : list) -> "FlowState":
        new_flow_state = self.copy()
        for change in changes:
            if type(change) is Balances:
                new_flow_state.balances = change
            elif type(change) is MintStatus:
                new_flow_state.mint_status = change
            elif type(change) is RedemptionStatus:
                new_flow_state.redemption_status = change
            elif type(change) is list and len(change) > 0:
                new_flow_state.pool_holdings = change
        new_flow_state.pool_holdings = sorted(self.pool_holdings, key=lambda ph: ph.pool_address)
        return new_flow_state
    
    def fields(self) -> list[str]:
        return list(self.__dataclass_fields__.keys())
    
    def __getitem__(self, key: str):
        return getattr(self, key)
    
    def copy(self) -> "FlowState":
        return FlowState(
            balances=self.balances.copy(),
            mint_status=self.mint_status.copy(),
            redemption_status=self.redemption_status.copy(),
            pool_holdings=self.pool_holdings.copy()
        )
    
    def compare(self, others: Union[list["FlowState"], "FlowState"]) -> list[dict]:
        if not isinstance(others, list):
            others = [others]
        all_mismatches = []
        for other in others:
            mismatches = {}
            for field in self.fields():
                v1 = self[field]
                v2 = other[field]
                if v1 != v2:
                    mismatches[field] = (v1, v2)
            all_mismatches.append(mismatches)
        return all_mismatches
    

@dataclass
class AgentInfo:
    address: str
    max_lots: int
    fee: int # in BIPS


# helper functions

def _repr_none_filtered(obj: Any) -> str:
    field_strs = [
        f"{k}={repr(v)}"
        for k, v in obj.__dict__.items()
        if v is not None
    ]
    return f"{obj.__class__.__name__}({', '.join(field_strs)})"