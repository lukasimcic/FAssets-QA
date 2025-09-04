from utils.user_bot import UserBot
from utils.config import *
import random
import time
import threading

# TODO: join all flows in one class as subclasses or organize differently

def mint_redeem_flow(
    token_fasset,
    num=0, 
    random_agent=True,
    log_steps=True, config=None, total_time=None, time_wait=60, timeout=None
):
    """
    This function will demonstrate a mint and redeem flow of a user bot.
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
    executor = UserBot(token_fasset, num, config)
    executor.logger.info(f"----- Mint and Redeem Flow -----")
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
            executor.mint(lot_amount, agent=agent, log_steps=log_steps, timeout=timeout)

        elif action == "redeem":
            lot_amount = random.randint(1, balances[token_fasset] // lot_size)
            executor.redeem(lot_amount, log_steps=log_steps, timeout=timeout)

        elif action == "mint_execute":
            mint_id = random.choice(mint_status["PENDING"])
            executor.execute_mint(mint_id, log_steps=log_steps, timeout=timeout)

        elif action == "redeem_default":
            redemption_id = random.choice(redemption_status["DEFAULT"])
            executor.redeem_default(redemption_id, log_steps=log_steps, timeout=timeout)

        time.sleep(time_wait)
        if total_time:
            total_time -= time.time() - t

            if total_time <= 0:
                executor.logger.info("--- Total time reached, stopping flow. ---")
                break
            else:
                executor.logger.info(f"--- Step finished, time left: {total_time:.2f} seconds. ---")

def pool_flow(
    token_fasset,
    num=0,
    log_steps=True, config=None, total_time=None, time_wait=60, timeout=None
):
    """
    This function will demonstrate a flow of a user bot interacting with collateral pools.
    It will repeatedly choose at random one of the following actions, if possible:
        - enter_pool: Enter a random pool with a random possible amount.
        - exit_pool: Exit a random (valid) pool with a random possible amount.
        - withdraw_pool_fees: Withdraws the fees from the a random (valid) pool.
    """

    executor = UserBot(token_fasset, num, config)
    executor.logger.info(f"----- Pool Flow -----")
    t = time.time()
    while True:
        pools = executor.get_pools(timeout=timeout)
        pool_holdings = executor.get_pool_holdings(timeout=timeout)
        balances = executor.get_balances(timeout=timeout)

        actions = []
        if pools and balances[token_underlying] > 0:
            actions.append("enter_pool")
        if pool_holdings:
            actions.append("exit_pool")
            actions.append("withdraw_pool_fees")
        action = random.choice(actions) if actions else None

        if action == "enter_pool":
            pool = random.choice(pools)
            amount = random.uniform(0, balances[token_native])
            executor.enter_pool(pool["Pool address"], amount, log_steps=log_steps, timeout=timeout)

        elif action == "exit_pool":
            pool = random.choice(pool_holdings)
            amount = random.uniform(0, pool["Pool tokens"])
            executor.exit_pool(pool["Pool address"], amount, log_steps=log_steps, timeout=timeout)

        elif action == "withdraw_pool_fees":
            pool = random.choice(pool_holdings)
            executor.withdraw_pool_fees(pool["Pool address"], log_steps=log_steps, timeout=timeout)

        time.sleep(time_wait)
        if total_time:
            total_time -= time.time() - t

            if total_time <= 0:
                executor.logger.info("--- Total time reached, stopping flow. ---")
                break
            else:
                executor.logger.info(f"--- Step finished, time left: {total_time:.2f} seconds. ---")

if __name__ == "__main__":
    
    threads = []
    for i in range(num_user_bots):
        t = threading.Thread(
            target=pool_flow, 
            args=(token_fasset,), 
            kwargs={"num": i, "total_time": 100}
            )
        threads.append(t)

    # Start each thread
    for t in threads:
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()
