from web3 import Web3
from pathlib import Path
import json
from eth_abi import decode
import binascii

# padding

def pad_to_64_hex(data: str) -> str:
    return data.ljust(64, "0")

def pad_to_40_hex(data: str) -> str:
    return data.ljust(40, "0")

def pad_0x(data: str) -> str:
    if not data.startswith("0x"):
        return "0x" + data
    return data

def unpad_0x(data: str) -> str:
    if data.startswith("0x"):
        return data[2:]
    return data

# converting

def to_hex(data: str) -> str:
    result = ""
    for char in data:
        result += format(ord(char), "x")
    return pad_to_64_hex(result)

def to_utf8_hex_string(data: str) -> str:
    return pad_0x(to_hex(data))

def keccak256_hexstr(data: str) -> str:
    return Web3.keccak(hexstr=data).hex()

def keccak256_text(data: str) -> str:
    return Web3.keccak(text=data).hex()

# error decoding

def error_encode(error_name: str) -> str:
    return pad_0x(keccak256_text(f"{error_name}()")[:8])

def get_error(error_names: list[str], encoded_error: str) -> str:
    for name in error_names:
        encoded_name = error_encode(name)
        if encoded_name == encoded_error:
            return name
    return "Error not in list."

# example folder: "fasset-bots/packages/fasset-bots-core/artifacts/contracts/assetManager/facets"
def save_errors(folder: Path) -> None:
    error_file = Path(__file__).parent / "errors.json"
    if error_file.exists() and error_file.stat().st_size > 0:
        with open(error_file, "r") as f:
            errors = json.load(f)
    else:
        errors = {}
    for subfolder in folder.iterdir():
        with open(subfolder, "r") as f:
            contract_abi = json.load(f)["abi"]
            for item in contract_abi:
                if item["type"] == "error":
                    error_name = item["name"]
                    encoded_error = error_encode(error_name)
                    errors[error_name] = encoded_error
    with open(error_file, "w") as f:
        json.dump(errors, f, indent=4)

def decode_revert_reason(data: str) -> str:
    error_data = data[10:] # remove '0x' and selector (8 chars after '0x')
    error_bytes = binascii.unhexlify(error_data)
    decoded = decode(['string'], error_bytes)
    print(decoded[0])