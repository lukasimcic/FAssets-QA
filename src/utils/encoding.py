from web3 import Web3

# padding

def pad_to_64_hex(data: str) -> str:
    return data.ljust(64, "0")

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
    return keccak256_text(f"{error_name}()")[:10]

def get_error(error_names: list[str], encoded_error) -> str:
    for name in error_names:
        encoded_name = error_encode(name)
        if encoded_name == encoded_error:
            return name
    return "Error not in list."