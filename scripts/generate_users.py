import toml
import typer
from src.flow.user_manager import UserManager
from src.utils.data_structures import TokenNative, TokenUnderlying

config = toml.load("config.toml")
token_native = TokenNative[config["token"]["native"]]
token_underlying = TokenUnderlying[config["token"]["underlying"]]


def main(num_new_users: int):
    um = UserManager(token_native, token_underlying)
    if not um.funder_exists():
        print("Generating funder user...")
        um.generate(funder=True)
    if num_new_users >= 1:
        print(f"Generating {num_new_users} new user{'s' if num_new_users > 1 else ''} with {token_native.name} and {token_underlying.name} addresses...")
        for _ in range(num_new_users):
            um.generate()

if __name__ == "__main__":
    typer.run(main)

    