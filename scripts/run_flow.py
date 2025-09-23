from src.flow.flow import Flow
from src.utils.config import num_user_bots, token_fasset
from src.flow.flow_actions import FlowActions
import inspect
import threading

all_actions = [
    name for name, _ in inspect.getmembers(FlowActions, predicate=inspect.isfunction)
    if not name.startswith("_")
]
bot_actions = [["scenario_2"] for _ in range(num_user_bots)] # can customize actions for each bot here

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