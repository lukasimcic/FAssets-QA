from src.flow.flow import Flow
from src.utils.config import num_user_bots, token_fasset
import threading

all_actions = ["mint", "mint_random", "redeem", "mint_execute", "redeem_default", "enter_pool", "exit_pool", "withdraw_pool_fees"]
bot_actions = [all_actions for _ in range(num_user_bots)] # can customize actions for each bot here

def make_threads(bot_actions):
    threads = []
    for i in range(num_user_bots):
        actions = bot_actions[i]
        flow = Flow(token_fasset, num=i, actions=actions, total_time=300)
        t = threading.Thread(target=flow.run)
        threads.append(t)
    return threads

if __name__ == "__main__":
    threads = make_threads(bot_actions)
    for t in threads:
        t.start()
    for t in threads:
        t.join()