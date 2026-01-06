import random
import threading
import time
from src.flow.flow import Flow
from src.actions import ACTION_BUNDLE_CLASSES
from src.utils.data_structures import UserData, TokenNative, TokenUnderlying
from src.flow.user_manager import UserManager
ALL_ACTIONS = [cls.__name__ for cls in ACTION_BUNDLE_CLASSES]

# configuration
token_native = TokenNative.C2FLR
token_underlying = TokenUnderlying.testXRP
user_nums = list(range(4))
request_funds = False
cli = False
total_time = 100
actions = [
    ALL_ACTIONS for _ in user_nums
]


def make_threads(actions):
    threads = []
    for i in user_nums:
        flow = Flow(
            UserData(
                token_native=token_native,
                token_underlying=token_underlying,
                num=i
            ),
            actions=actions[i],
            cli=cli,
            total_time=total_time,
            time_wait=5
            )
        t = threading.Thread(target=flow.run)
        threads.append(t)
    return threads

if __name__ == "__main__":
    um = UserManager(token_native, token_underlying, user_nums=user_nums)
    if request_funds:
        um.request_funds()
    um.distribute_funds()
    threads = make_threads(actions)
    for t in threads:
        time.sleep(random.uniform(3, 3.5))
        t.start()
    for t in threads:
        t.join()
    um.collect_funds()