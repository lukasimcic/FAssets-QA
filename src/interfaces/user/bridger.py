from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from eth_abi import encode
from eth_utils import to_checksum_address
from src.interfaces.contracts.asset_manager import AssetManager
from src.interfaces.contracts.fasset_oft_adapter import FAssetOFTAdapter
from src.interfaces.contracts.fasset import FAsset
from src.interfaces.network.networks.native_networks.native_network import NativeNetwork
from src.interfaces.network.networks.external_networks.HyperEVM_testnet import HyperEVM_testnet
from src.interfaces.network.networks.external_networks.HyperCore_testnet import HyperCore_testnet
from src.interfaces.network.networks.underlying_networks.underlying_network import UnderlyingNetwork
from src.interfaces.network.networks.underlying_networks.XRPL_testnet import XRPL_testnet
from src.interfaces.user.user import User
from src.utils.encoding import pad_left_to_64_hex, pad_0x, unpad_0x
if TYPE_CHECKING:
    from src.interfaces.network.networks.external_networks.external_network import ExternalNetwork
    from src.flow.fee_tracker import FeeTracker
    from src.utils.data_structures import UserData
    from src.flow.fee_tracker import FeeTracker


class Bridger(User):
    def __init__(self, user_data : "UserData", fee_tracker : Optional["FeeTracker"]  = None):
        super().__init__(user_data, fee_tracker)

    def _approve_tokens(self, spender: str, lots: int, composer: bool = True) -> None:
        lot_size = AssetManager(self.native_network, self.token_fasset).lot_size()
        amount_uba = self.token_fasset.to_uba(Decimal(lots * lot_size))
        f = FAsset(self.native_network, self.token_fasset, self.native_credentials, self.fee_tracker)
        f.approve(spender, amount_uba)
        if composer:
            f.approve(self.native_network.composer_address(), amount_uba)
    
    def _get_send_params(
            self, 
            to_eid: int, 
            to_address: str, 
            amount_uba: int, 
            extra_options: bytes,
            compose_msg: bytes = b"",
            oft_cmd: bytes = b""
            ) -> dict:
        return {
            "dstEid": to_eid,
            "to": pad_0x(pad_left_to_64_hex(unpad_0x(to_address))),
            "amountLD": amount_uba,
            "minAmountLD": amount_uba,
            "extraOptions": extra_options,
            "composeMsg": compose_msg,
            "oftCmd": oft_cmd,
        }
    
    def _get_underlying_fee(self, lots: int) -> Decimal:
        FEE_PER_LOT = {
            XRPL_testnet.coin: Decimal("0.05")
        }
        return FEE_PER_LOT[self.underlying_network.coin] * Decimal(lots)

    def _bridge(
            self, 
            from_network: type["NativeNetwork"] | type["ExternalNetwork"],
            to_network: type["NativeNetwork"] | type["ExternalNetwork"] | type["UnderlyingNetwork"],
            lots: int,
            log_steps: bool = False
        ) -> dict:

        # prepare send parameters
        lot_size = AssetManager(self.native_network, self.token_fasset).lot_size()
        amount_uba = self.token_fasset.to_uba(Decimal(lots * lot_size))
        foa = FAssetOFTAdapter(
            from_network, 
            self.token_fasset, 
            self.native_credentials, 
            self.fee_tracker
            )
        match to_network:

            case _ if to_network is HyperCore_testnet: # via HyperEVM_testnet
                to_eid = HyperEVM_testnet.eid()
                extra_options = foa.combine_options(to_eid)
                extra_options += bytes.fromhex("010013030000000000000000000000000000000493e0") # addExecutorComposeOption(0, 300_000, 0)
                compose_msg = encode(
                    ["uint256", "address"],
                    [0, to_checksum_address(self.native_credentials.address)]
                )
                send_params = self._get_send_params(
                    to_eid=to_eid, 
                    to_address=HyperEVM_testnet.composer_address(), 
                    amount_uba=amount_uba, 
                    extra_options=extra_options,
                    compose_msg=compose_msg
                    )
                
            case _ if issubclass(to_network, UnderlyingNetwork): # auto-redeem
                to_eid = self.native_network.eid()
                extra_options = foa.combine_options(to_eid)
                extra_options += bytes.fromhex("010013030000000000000000000000000000000f4240") # addExecutorComposeOption(0, 1_000_000, 0)
                compose_msg = encode(
                    ["uint256", "string", "address", "address"],
                    [amount_uba, self.underlying_credentials.address, self.native_credentials.address, self.native_network.zero_address()]
                )
                send_params = self._get_send_params(
                    to_eid=to_eid, 
                    to_address=self.native_network.composer_address(), 
                    amount_uba=amount_uba, 
                    extra_options=extra_options,
                    compose_msg=compose_msg
                    )
                
            case _:
                to_eid = to_network.eid()
                send_params = self._get_send_params(
                    to_eid=to_eid, 
                    to_address=self.native_credentials.address, 
                    amount_uba=amount_uba, 
                    extra_options=foa.combine_options(to_eid)
                    )
        self.log_step(
            f"LayerZero send parameters: {dict(send_params, extraOptions='0x' + send_params['extraOptions'].hex(), composeMsg='0x' + send_params['composeMsg'].hex())}", 
            log_steps=log_steps
            )

        # get fees and send
        fee_uba = foa.quote_fee(send_params, False)
        fee = from_network().coin.from_uba(fee_uba)
        self.fee_tracker.update_fees(from_network().coin, other_fees=fee)
        result_dict = foa.send(send_params, fee_uba, 0, self.native_credentials.address)
        self.log_step(f"LayerZero transaction 0x{result_dict['receipt']['transactionHash'].hex()} sent.", log_steps=log_steps)
        return result_dict
    
    def bridge_to(self, network: type["ExternalNetwork"], lots: int, log_steps: bool = False) -> dict:
        self.log_step("Approving tokens for bridge ...", log_steps=log_steps)
        foa = FAssetOFTAdapter(
            self.native_network, 
            self.token_fasset
            )
        self._approve_tokens(foa.address, lots)
        self.log_step(f"Approved {lots} lots for {foa.address}.", log_steps=log_steps)
        return self._bridge(self.native_network, network, lots, log_steps=log_steps)
    
    def bridge_from(self, network: type["ExternalNetwork"], lots: int, log_steps: bool = False) -> dict:
        return self._bridge(network, self.native_network, lots, log_steps=log_steps)

    def auto_redeem_from(self, network: type["ExternalNetwork"], lots: int, log_steps: bool = False) -> dict:
        send_dict = self._bridge(network, self.underlying_network, lots, log_steps=log_steps)
        underlying_fee = self._get_underlying_fee(lots)
        self.fee_tracker.update_fees(self.underlying_network.coin, other_fees=underlying_fee)
        return send_dict