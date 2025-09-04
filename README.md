# FAssets-QA

## Simple tests

Introductory tests are stored in folder `tests`.
Contents include:

  - `flows.py` implements different flows of user actions:
    - `mint_redeem_flow` repeatedly chooses at random one of the following actions, if possible:
      - mint: Mint a random amount of lots from the underlying token.
      - redeem: Redeem a random amount of lots from the fasset token.
      - mint_execute: Execute a pending mint.
      - redeem_default: Redeem a default redemption.
    - `pool_flow` repeatedly chooses at random one of the following actions, if possible:
      - enter_pool: Enter a random pool with a random possible amount.
      - exit_pool: Exit a random (valid) pool with a random possible amount.
      - withdraw_pool_fees: Withdraw the fees from a random (valid) pool.

  - `utils/user_bot.py` implements a class UserBot that interacts with CLI and simulates a user on the network.
    It provides methods to execute commands and parse their output.

  - `utils/config.py` provides configuration constants used throughout the test scripts
