import random
import threading
import time
from typing_extensions import Annotated
from dotenv import load_dotenv
load_dotenv()
import toml
import typer
from src.interfaces.network.tokens import TokenNative, TokenUnderlying
from src.flow.flow import Flow
from src.actions import ACTION_BUNDLE_CLASSES
from src.utils.data_structures import UserData
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

def parse_action_params(action_params_list: list[str]) -> dict[str, dict]:
    action_params = {}
    for item in action_params_list:
        try:
            action_name, params_str = item.split(":", 1)
            params = dict(param.split("=") for param in params_str.split(",") if "=" in param)
            action_params[action_name] = params
        except ValueError:
            print(f"Invalid action parameter format: {item}. Expected format: 'ActionName:param1=value1,param2=value2'")
    return action_params


def make_threads(action_params, total_time, cli):
    threads = []
    for i in user_nums:
        flow = Flow(
            UserData(
                token_native=token_native,
                token_underlying=token_underlying,
                num=i
            ),
            actions=actions[i],
            action_params=action_params,
            cli=cli,
            total_time=total_time,
            time_wait=5
            )
        t = threading.Thread(target=flow.run)
        threads.append(t)
    return threads

def main( 
        request_funds: bool = False, 
        action_params: Annotated[list[str] | None, typer.Option()] = None,
        cli: bool = False
    ):
    um = UserManager(token_native, token_underlying, user_nums=user_nums)
    if request_funds:
        um.request_funds()
    um.distribute_funds()
    action_params = parse_action_params(action_params) if action_params else {}
    threads = make_threads(action_params, run_time, cli)
    for t in threads:
        time.sleep(random.uniform(3, 3.5))
        t.start()
    for t in threads:
        t.join()
    um.collect_funds()

if __name__ == "__main__":
    typer.run(main)