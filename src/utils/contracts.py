import json
from typing import Optional, TYPE_CHECKING
import toml
from pathlib import Path
if TYPE_CHECKING:
    from src.interfaces.contracts.contract_client import ContractClient
    from src.interfaces.network.networks.external_networks.external_network import ExternalNetwork
    from src.interfaces.network.networks.native_networks.native_network import NativeNetwork
    from src.interfaces.network.tokens import TokenFAsset

config = toml.load("config.toml")
contract_interfaces_folder = config["folder"]["contract_interfaces"]


def get_contract_names(cl: "ContractClient", token_fasset: Optional["TokenFAsset"] = None) -> str:
    name = cl.__class__.__name__
    names = {"instance": name, "interface": name}
    if token_fasset:
        names["instance"] += f"_{token_fasset.name}"
    return names

def get_contract_address(instance_name: str, network: "NativeNetwork | ExternalNetwork") -> str:
    with open(network.contracts_file(), "r") as f:
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
