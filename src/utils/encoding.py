def to_hex(data: str) -> str:
    result = ""
    for char in data:
        result += format(ord(char), "x")
    return result.ljust(64, "0")

def to_utf8_hex_string(data: str) -> str:
    return "0x" + to_hex(data)