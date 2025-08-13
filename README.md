# FAssets-QA

## Simple tests

Some introductory simple tests are stored in folder `simple_tests`.
Contents include:

  - `mint_redeem_flow.py`
    This function will demonstrate a mint and redeem flow of a user.
    It will repeatedly choose at random one of the following actions, if possible:
    - mint: Mint a random amount of lots from the underlying token.
    - redeem: Redeem a random amount of lots from the fasset token.
    - mint_execute: Execute a pending mint.
    - redeem_default: Redeem a default redemption.

  - `utils/user_bot.py` implements a class UserBot that interacts with CLI and simulates a user on the network.
    It provides methods to execute commands and parse their output.
