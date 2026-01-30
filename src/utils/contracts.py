import json
from typing import Optional
import toml
from pathlib import Path
from src.utils.data_structures import TokenBridged, TokenFasset, TokenNative, TokenUnderlying, TokenUnderlying
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.interfaces.contracts.contract_client import ContractClient

config = toml.load("config.toml")
contract_interfaces_folder = config["folder"]["contract_interfaces"]


def get_contract_names(cl: "ContractClient", token_underlying: Optional[TokenUnderlying] = None) -> str:
    name = cl.__class__.__name__
    names = {"instance": name, "interface": name}
    if token_underlying:
        token_fasset = TokenFasset.from_underlying(token_underlying)
        names["instance"] += f"_{token_fasset.name}"
    return names

def get_contract_address(instance_name: str, token_native: TokenNative | TokenBridged) -> str:
    with open(token_native.contracts_file, "r") as f:
        contracts = json.load(f)
    for contract in contracts:
        if contract.get("name") == instance_name:
            return contract.get("address")
    raise ValueError(f"Contract {instance_name} not found")

def get_contract_abi(interface_name: str) -> list:
    contract_path = Path(contract_interfaces_folder) / f"{interface_name}.json"
    with open(contract_path, "r") as f:
        return json.load(f)["abi"]

def get_output_index(contract_interface_name: str, function_name: str, output_name: str) -> int:
    abi = get_contract_abi(contract_interface_name)
    try:
        for item in abi:
            if item.get("type") == "function" and item.get("name") == function_name:
                outputs = item.get("outputs")[0].get("components")
                for index, output in enumerate(outputs):
                    if output.get("name") == output_name:
                        return index
    except Exception as e:
        raise ValueError(f"Function {function_name} not found in contract {contract_interface_name}: {e}")
