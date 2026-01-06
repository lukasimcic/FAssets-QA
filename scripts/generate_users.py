from src.flow.user_manager import UserManager
from src.utils.data_structures import TokenNative, TokenUnderlying

# configuration
token_native = TokenNative.C2FLR
token_underlying = TokenUnderlying.testXRP
num_new_users = 1


if __name__ == "__main__":
    um = UserManager(token_native, token_underlying)
    if not um.funder_exists():
        print("Generating funder user...")
        um.generate(funder=True)
    if num_new_users >= 1:
        print(f"Generating {num_new_users} new user{'s' if num_new_users > 1 else ''} with {token_native.name} and {token_underlying.name} addresses...")
        for i in range(num_new_users):
            um.generate()
    