import random
import threading
import time
from dotenv import load_dotenv
load_dotenv()
import toml
import typer
from src.flow.flow import Flow
from src.actions import ACTION_BUNDLE_CLASSES
from src.utils.data_structures import UserData, TokenNative, TokenUnderlying
from src.flow.user_manager import UserManager
from src.utils.secrets import get_user_nums

ALL_ACTIONS = [cls.__name__ for cls in ACTION_BUNDLE_CLASSES]
config = toml.load("config.toml")
token_native = TokenNative[config["token"]["native"]]
token_underlying = TokenUnderlying[config["token"]["underlying"]]
run_time = config["flow"]["run_time"]
user_nums = config["flow"]["user_nums"] if config["flow"]["user_nums"] else get_user_nums()
actions = config["flow"]["actions"] if config["flow"]["actions"] else [
    ALL_ACTIONS for _ in user_nums
    ]


def make_threads(total_time, cli):
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

def main( 
        request_funds: bool = False, 
        cli: bool = False
    ):
    um = UserManager(token_native, token_underlying, user_nums=user_nums)
    if request_funds:
        um.request_funds()
    um.distribute_funds()
    threads = make_threads(run_time, cli)
    for t in threads:
        time.sleep(random.uniform(3, 3.5))
        t.start()
    for t in threads:
        t.join()
    um.collect_funds()

if __name__ == "__main__":
    typer.run(main)