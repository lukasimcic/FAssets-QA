# FAssets-QA

## Simple tests

Introductory tests are stored in folder `tests`.
Contents include:

  - `flow.py` implements different flows of user actions. 
    When running the script, multiple user bots operate in parallel, each repeatedly selecting a random action from the following:
    - mint: Mint a random amount of lots from the underlying token.
    - redeem: Redeem a random amount of lots from the fasset token.
    - mint_execute: Execute a pending mint.
    - redeem_default: Redeem a default redemption.
    - enter_pool: Enter a random pool with a random possible amount.
    - exit_pool: Exit a random (valid) pool with a random possible amount.
    - withdraw_pool_fees: Withdraw the fees from a random (valid) pool.

  - `utils/user_bot.py` implements a class UserBot that interacts with CLI and simulates a user on the network.
    It provides methods to execute commands and parse their output.

  - `utils/contract_client.py` implements a class ContractClient that interacts directly with contracts in the FAsset system.

  - `utils/config.py` provides configuration constants used throughout the test scripts.
