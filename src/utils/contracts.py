from config.config_qa import coston2_contracts_file
import json

def get_contract_address(contract_instance_name: str, native_network: str = "C2FLR") -> str:
    if native_network == "C2FLR":
        contracts = coston2_contracts_file
    else:
        raise ValueError(f"Unsupported native network: {native_network}.")
    with open(coston2_contracts_file, "r") as f:
        coston2_contracts = json.load(f)
    for contract in coston2_contracts:
        if contract.get("name") == contract_instance_name:
            return contract.get("address")
    raise ValueError(f"Contract {contract_instance_name} not found")

def get_contract_abi(contract_path: str) -> list:
    with open(contract_path, "r") as f:
        return json.load(f)["abi"]

def get_output_index(contract_path: str, function_name: str, output_name: str) -> int:
    abi = get_contract_abi(contract_path)
    try:
        for item in abi:
            if item.get("type") == "function" and item.get("name") == function_name:
                outputs = item.get("outputs")[0].get("components")
                for index, output in enumerate(outputs):
                    if output.get("name") == output_name:
                        return index
    except Exception as e:
        raise ValueError(f"Function {function_name} not found at {contract_path}: {e}")
