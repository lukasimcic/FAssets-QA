# FAssets-QA

This repository contains a testing framework for FAssets protocol. It allows simulating multiple users performing various actions (minting, redeeming, interacting with collateral pools,...) in parallel, to test the protocol under load and ensure its correctness.

## Instructions

1. Setup environment: 
  - Virtual environment with python 3.11 is recommended.
  - Clone this repository.
  - Run `git submodule update --init --recursive` to clone fasset-bots submodule.
  - Run `pip install -r requirements.txt` to install dependencies.
2. Configure the environment:
  - Copy `.env.template` to `.env` and set bot credentials if needed (see below).
  - If needed, modify configuration parameters in `config.toml` (see below). 
2. Generate users and a funder: 
  - Run `python -m scripts.generate_users n` where n is the number of users to generate.
3. Run the user flow:
  - Run `python -m scripts.run_flow` (see below for possible parameters).


### Parameters

The whole framework is dependent on two main parameters: native network and underlying network (instances of NativeToken and UnderlyingToken classes). These are set in `config.toml` file. For now only `"C2FLR"` (native) and `"testXRP"` (underlying) networks are supported.

In `config.toml`, under `[bot]` section, you can change the parameter `level` to set the bot message level. Possible values are: `"info"`, `"warning"`, `"error"`. Only messages with level equal or higher than the set level will be sent to the Telegram bot.

Under section `[flow]`, you can set the following parameters:
- `run_time`: Total duration in seconds for which each user should execute actions in the flow.
- `user_nums`: List of user indices (integers starting at 0) to include in the flow. Users must already be generated. If left empty, all generated users will be included.
- `actions`: List of action class names to include in the flow for each user. If left empty, all action classes are included for each user. You can customize this list per user if needed, for example for 2 users:
```
actions = [
    ["RedeemRandomAmount", "WithdrawRandomPoolFees"],
    ["Scenario2"],
]
```
In this case, user 0 will only choose between `RedeemRandomAmount` and `WithdrawRandomPoolFees` actions and user 1 will only execute `Scenario2` action.

In `.env` file, set the given environment variables to configure the Telegram bot for notifications. Otherwise, leave them empty to disable bot notifications. For obtaining a bot token, follow instructions in [this guide](https://core.telegram.org/bots/features#creating-a-new-bot). Then, create a channel, add the bot as an admin to the channel and obtain the channel ID.

When running the `run_flow.py` script, additional parameters can be set via command line arguments:
- `--request-funds`: The funder should request new funds at the start of the flow.
- `--cli`: Run the flow in CLI mode. CLI mode uses bots defined in fasset-bots submodule. Not all actions are supported in CLI mode. See below for details.

If `request_funds` is set to True, new funds for both native and underlying tokens will be requested from faucets at the start of the flow. Because Coston2 faucet has no API support, manual intervention is needed to complete the funding process. For this, follow the instructions printed in the console to complete the funding process.

## Flow

When running `python -m scripts.run_flow`, the following occurs:
1. The funder funds each user with initial native and underlying tokens.
2. Each user starts repeatedly executing actions in parallel threads for a specified duration.
3. The funder collects funds back from users at the end.

### Actions

Each user repeatedly selects a random action from the following:

| Action name | Procedure       | CLI supported |
|-------------|-----------------|---------------|
| MintRandomAgentRandomAmount | Mint a random amount of lots against a random agent. | Yes |
| MintLowestFeeAgentRandomAmount | Mint a random amount of lots against an agent with lowest fee. | Yes |
| MintExecuteRandomMinting | Execute a random pending mint. | Yes |
| MintRandomAgentRandomAmountBlockUnderlying | - Block all underlying deposits. <br>- Mint a random amount of lots against a random agent. <br>- Unblock all underlying deposits. | No |
| RedeemRandomAmount | Redeem a random amount of lots. | Yes |
| RedeemDefaultRandomRedemption | Redeem a random default redemption. | Yes |
| RedeemDefaultRandomRedemptionBlockUnderlying | - Block all underlying deposits. <br>- Redeem a random amount of lots. <br>- Unblock all underlying deposits. | No |
| EnterRandomPoolRandomAmount | Enter a random pool with a random amount. | Yes |
| ExitRandomPoolRandomAmount | Exit a random (valid) pool with a random amount. | Yes |
| WithdrawRandomPoolFees | Withdraw a random amount of fees from a random (valid) pool. | Yes |
| Scenario1 | - Enter a random pool with a random amount. <br>- Mint a random amount of lots against the agent that owns the entered collateral pool. <br>- Redeem the amount minted. <br>- Wait for the collateral pool token timelock period to expire. <br>- If possible, exit pool with all tokens. <br>- If possible, withdraw pool fees. | Yes |
| Scenario2 | - Enter a random pool with a random amount. <br>- Wait for the collateral pool token timelock period to expire. <br>- Transfer debt-free pool tokens (up to the amount originally entered) to the partner user bot. <br>- Exit pool from the partner user bot. |  No  |

Each action is implemented as an "action bundle" class in `src/actions/`. Each bundle consists of:
- condition: Checks to determine if the action can be executed.
- action: Steps to perform the action.
- expected_state: Expected state (balances, pool holdings, redemption and minting status) of the user after action execution

At every step, one action is randomly selected from the list of possible actions whose conditions are met. After execution, the actual user state is compared against the expected state to verify correctness. In user's log file, detailed information about the flow are provided.

### CLI mode

When running in CLI mode, all user actions are executed via bots implemented in fasset-bots submodule. In both cases (CLI and non-CLI), same action logic is being used, just different CoreAction classes are called (see `src/actions/core_actions`).

CLI mode is limited and not advised for load testing. That is because:
- Not all actions and scenarios are supported in CLI mode.
- Load testing is very resource-intensive for the server. For such purposes, a low-level approach with direct contract interaction is more appropriate.

For these reasons, **CLI mode has not yet been tested for load testing**.

For using fasset-bots submodule for specific actions of a user, follow instructions in `fasset-bots/README.md`. Make sure to first generate user(s) and set the environment variables to point to correct user config and secrets files. This is done by creating a `.env` file in `fasset-bots/` directory with the following content (n is the user index, for example 0):

```
FASSET_BOT_CONFIG="./packages/fasset-bots-core/run-config/coston2-bot.json" 
FASSET_USER_SECRETS="../secrets/user/user_n.json"
FASSET_USER_DATA_DIR="../data/data_storage/user/user_n/"
```

## Project Structure Overview

```
├── scripts/                            # Entry points
│   ├── run_flow.py                     # Main script to run user flows
│   └─── generate_users.py               # Script for new users and funder generation
├── src/
│   ├── actions/                        
│   │   ├── core_actions/               # Core actions (mint, redeem, enter pool,...)
│   │   ├── action_bundle.py            # Base class for action bundles
│   │   ├── helper_functions.py         # Shared helper functions for all actions
│   │   ├── mint.py, pool.py, redeem.py # Minting, pool, redeeming action bundles for minting
│   │   └── scenarios/                  # Scenario action bundles
│   ├── flow/                           
│   │   ├── fee_tracker.py              # Tracker of gas/fee usage during flow (see below)
│   │   ├── flow.py                     # Main flow logic
│   │   └── user_manager.py             # User and funder management
│   ├── interfaces/                     
│   │   ├── contracts/                  # Contract interaction (see below) 
│   │   ├── network/                    # Network interaction (see below)
│   │   └── user/                       # User abstractions (see below)
│   └── utils/                          # Utilities and shared code
├── user_data/
│   ├── data_storage/                   # Storage of active mintings and redeptions (see below)
│   ├── secrets/                        # Secrets for users and partners (see below)
│   └── logs/                           # Log files for funder, users, and partners (see below)
├── config.toml                         # Non-sensitive configuration
├── .env                                # Sensitive configuration
└── requirements.txt                    # Python dependencies
```

### Network interaction

Each native/underlying network is a subclass of NativeNetwork/UnderlyingNetwork in `src/interfaces/network/`. Each subclass implements methods for network-specific operations (e.g., sending transactions, checking balances, etc.). Each network instance is dependent on user data (UserData subclass).

Although the framework is designed to be extensible to multiple native and underlying networks, currently only Coston2 (native) and Flare (underlying) networks are supported.

### Contract interaction

Each contract is represented as a subclass of `ContractClient`. Each subclass implements methods for interacting with the specific contract's functions (e.g., minting, redeeming, entering/exiting pools, etc.). Each contract intance is dependent on a native network (NativeNetwork subclass) and optionally user native data (UserNativeData subclass, user's native credentials).

In the `addresses` folder, contract addresses for different networks are stored in JSON files. Each file contains addresses for all contracts deployed on a specific native network.

### User abstractions

All user types are sublasses of the `User` class. Each user subclass implements methods for user-specific operations (e.g., minting, redeeming, entering/exiting pools, etc.). Each user instance is dependent on user data (UserData subclass, consisting of information about native and underlying networks, and user identity).

User types:
- Minter: Responsible for minting related actions (minting lots, executing pending mintings, obtaining minting status).
- Redeemer: Responsible for redeeming related actions (redeeming lots, executing default redeptions, obtaining redemption status).
- PoolManager: Responsible for collateral pool related actions (entering/exiting pools, withdrawing fees, obtaining pool holdings and pools, transfering pool tokens).
- StateManager: Used to obtain user info (balances).
- Funder: Responsible for funding users and collecting funds back.
- UserBot: Bot user for CLI mode, using fasset-bots submodule. When in CLI mode all functionalities are provided by UserBot and no other user subclasses are used.

Each user that is executing actions also has a corresponding partner user used for specific scenarios (e.g., transferring pool tokens). Both users and partner users call classes described above as needed. For example, if user 1 is executing Scenario 2, it will call PoolManager methods to enter the pool and transfer tokens, and its partner user (user 1 partner) will call PoolManager methods to exit the pool after receiving the pool tokens.

### Fee tracker

Because the expected state is dependent on gas/fee usage, a FeeTracker class is implemented to keep track of gas/fee usage during the flow. Each user has its own FeeTracker instance. The FeeTracker is updated after one of the following events:
- Sending transactions on the underlying network.
- Using contract methods.

### Data storage

Active mintings and redeptions are stored in JSON files in `data/data_storage/` directory. They contain minting/redemption id and relevant information (e.g., amount, agent, status, etc.). Each user has its own minting and redemption storage files.

Mintings are stored until they are executed, which should happen in the same user action. However, in case of failures (e.g., network issues), mintings may remain unexecuted. User can then execute any stored pending mintings from previous runs.

After redeeming lots, user must wait for the redemption to be processed by an agent. In the meantime, redemption is stored and can only be processed by the user after it is defaulted. In this case, user can redeem any stored default redemptions from previous runs.

### Logs

Each user and funder has its own log file in `data/logs/` directory. Logs contain detailed information about each action executed, state changes, state mismatches (if any) and possible errors. At the end of the flow, a success rate is also provided.

### Secrets

After generating users and funder, their credentials are stored in JSON files in `data/secrets/` directory. Each user and funder has its own secrets file.


## Known Issues

- Sometimes expected state is (rightfully) not the same as the actual one, because pool fees increase a bit during an action execution.

- Expected state after redeeming does not account for possible redemption in other tokens (not underlying token).





