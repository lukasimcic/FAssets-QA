# FAssets-QA

## User flow

When running `python -m scripts.run_flow`, multiple user bots start operating in parallel.
Each bot repeatedly selects a random action from the following:
  - mint: Mint a random amount of lots against an agent with lowest fee.
  - mint_random: Mint a random amount of lots against a random agent.
  - redeem: Redeem a random amount of lots.
  - mint_execute: Execute a pending mint.
  - redeem_default: Redeem a default redemption.
  - enter_pool: Enter a random pool with a random amount.
  - exit_pool: Exit a random (valid) pool with a random amount.
  - withdraw_pool_fees: Withdraws fees from a random (valid) pool.
  - specific scenarios described below

### Scenarios

| Scenario number | Procedure       |
|-----------------|-----------------|
| 1               | - Enter a random pool with a random amount. <br>- Mint a random amount of lots against the agent that owns the entered collateral pool. <br>- Redeem the amount minted. <br>- Wait for the collateral pool token timelock period to expire. <br>- If possible, exit pool with all tokens. <br>- If possible, withdraw pool fees. |
| 2               | - Enter a random pool with a random amount. <br>- Wait for the collateral pool token timelock period to expire. <br>- Transfer debt-free pool tokens (up to the amount originally entered) to the partner user bot. <br>- Exit pool from the partner user bot. |

## Code structure

- Scripts in the `scripts/` directory serve as entry points for running flows and scenarios.

- The `src/flow/` directory contains the main flow logic, including:
  - `flow.py`: Defines the `Flow` class, which manages the sequence of user bot actions.
  - `flow_conditions.py`: Encapsulates the conditions under which actions can be performed.
  Each `Flow` instance has a `FlowConditions` instance as an attribute, which provides methods to check if specific actions are allowed based on the current state.
  - `flow_actions.py`: Encapsulates the actions that a user bot can perform within a flow.
  Each `Flow` instance has a `FlowActions` instance as an attribute, which provides methods to execute specific actions.
  
- The `src/clients/` directory contains classes for interacting with external systems:
  - `user_bot.py`: Implements the `UserBot` class for simulating user interactions via the command line interface.
  - `contract_client.py`: Implements the `ContractClient` class for direct interaction with smart contracts on the network.

- The `src/utils/` directory provides shared utilities and configuration:
  - `config.py`: Stores configuration constants and parameters.

