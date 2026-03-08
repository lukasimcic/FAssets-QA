import toml
import typer
from src.flow.user_manager import UserManager
from src.interfaces.network.tokens import TokenNative, TokenUnderlying

config = toml.load("config.toml")
token_native = TokenNative[config["token"]["native"]]
token_underlying = TokenUnderlying[config["token"]["underlying"]]


def main(
        num_new_users: int, 
        native_address: str = None, 
        native_private_key: str = None,
        underlying_address: str = None,
        underlying_public_key: str = None,
        underlying_private_key: str = None
        ):
    
    if native_address or native_private_key:
        if not (native_address and native_private_key):
            print("Both native_address and native_private_key must be provided together.")
            return
    if underlying_address or underlying_private_key:
        if not (underlying_address and underlying_public_key and underlying_private_key):
            print("Both underlying_address, underlying_public_key and underlying_private_key must be provided together.")
            return
    if (native_address and native_private_key) and (underlying_address and underlying_public_key and underlying_private_key):
        if num_new_users != 1:
            print("num_new_users must be 1 when providing credentials for a new user.")
            return
    
    secrets_native = None
    if native_address and native_private_key:
        secrets_native = {
            "address": native_address,
            "private_key": native_private_key
        }
    secrets_underlying = None
    if underlying_address and underlying_public_key and underlying_private_key:
        secrets_underlying = {
            "address": underlying_address,
            "public_key": underlying_public_key,
            "private_key": underlying_private_key
        }

    um = UserManager(token_native, token_underlying)
    if not um.funder_exists():
        print("Generating funder user...")
        um.generate(funder=True)
    if num_new_users >= 1:
        print(f"Generating {num_new_users} new user{'s' if num_new_users > 1 else ''} with {token_native.name} and {token_underlying.name} addresses...")
        for _ in range(num_new_users):
            um.generate(secrets_underlying=secrets_underlying, secrets_native=secrets_native)

if __name__ == "__main__":
    typer.run(main)

    