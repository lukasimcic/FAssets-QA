from utils.user_bot import UserBot
from utils.config import *
import random
import time

# TODO: Update print messages to accurately reflect the outcome of minting and redeeming actions,
#       indicating whether each operation succeeded or failed, rather than always assuming success.


def mint_redeem_flow(
    token_fasset, random_agent=True, total_time=None, time_wait=60, timeout=None
):
    """
    This function will demonstrate a mint and redeem flow.
    It will repeatedly choose at random one of the following actions, if possible:
        - mint: Mint a random amount of lots from the underlying token.
        - redeem: Redeem a random amount of lots from the fasset token.
        - mint_execute: Execute a pending mint.
        - redeem_default: Redeem a default redemption.

    If random_agent is set to True,
        mintings will be done against a random agent that has the capacity for minting enough lots.
    If random_agent is set to False,
        mintings will be done against an agent with lowest fee that has the capacity for minting enough lots.
    """
    executor = UserBot(token_fasset)
    t = time.time()
    while True:
        balances = executor.get_balances(timeout=timeout)
        mint_status = executor.get_mint_status(timeout=timeout)
        redemption_status = executor.get_redemption_status(timeout=timeout)

        actions = []
        if balances[token_underlying] >= lot_size:
            actions.append("mint")
        if balances[token_fasset] >= lot_size:
            actions.append("redeem")
        if mint_status["PENDING"]:
            actions.append("mint_execute")
        if redemption_status["DEFAULT"]:
            actions.append("redeem_default")

        action = random.choice(actions) if actions else None

        if action == "mint":
            lot_amount = random.randint(1, balances[token_underlying] // lot_size)
            agent = None
            # select an agent with enought max lots (if not provided)
            if random_agent:
                agents = []
                for agent in executor.get_agents():
                    if agent["max_lots"] * lot_size >= lot_amount:
                        agents.append(agent["address"])
                agent = random.choice(agents)
            try:
                executor.mint(
                    lot_amount, agent=agent, print_result=False, timeout=timeout
                )
                print(
                    f"Minted {lot_amount * lot_size} of {token_fasset} against agent {agent}"
                )
            except Exception as e:
                print(f"Error minting {lot_amount * lot_size} of {token_fasset}: {e}")

        elif action == "redeem":
            lot_amount = random.randint(1, balances[token_fasset] // lot_size)
            try:
                executor.redeem(lot_amount, print_result=False, timeout=timeout)
                print(f"Redeemed {lot_amount * lot_size} of {token_fasset}")
            except Exception as e:
                print(f"Error redeeming {lot_amount * lot_size} of {token_fasset}: {e}")

        elif action == "mint_execute":
            mint_id = random.choice(mint_status["PENDING"])
            try:
                executor.execute_mint(mint_id, timeout=timeout)
                print(f"Executed mint with id {mint_id}")
            except Exception as e:
                print(f"Error executing mint with id {mint_id}: {e}")

        elif action == "redeem_default":
            redemption_id = random.choice(redemption_status["DEFAULT"])
            try:
                executor.redeem_default(redemption_id, timeout=timeout)
                print(f"Redeemed default redemption with id {redemption_id}")
            except Exception as e:
                print(
                    f"Error redeeming default redemption with id {redemption_id}: {e}"
                )

        time.sleep(time_wait)
        if total_time:
            total_time -= time.time() - t
            print("---")
            print("Time left:", total_time)
            if total_time <= 0:
                print("Total time reached, stopping flow.")
                break

if __name__ == "__main__":
    mint_redeem_flow(token_fasset, random_agent=True, total_time=300)
