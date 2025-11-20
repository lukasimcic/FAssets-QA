from locust import User, between, task, events
from functools import wraps
from src.tasks.core_actions import CoreActions
from src.interfaces.contracts.asset_manager import AssetManager
from src.interfaces.user.informer import Informer
from src.interfaces.user.minter import Minter
from src.interfaces.user.pool_manager import PoolManager
from src.interfaces.user.redeemer import Redeemer
import src.tasks.conditions as conditions
from src.tasks.helper_functions import *
import random

@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--token-native", type=str, default="C2FLR")
    parser.add_argument("--token-underlying", type=str, default="testXRP")
    parser.add_argument("--user-nums", type=list[int], default=[0])
    parser.add_argument("--tasks", type=list[str], default=[])
    parser.add_argument("--log-steps", type=bool, default=True)


class Tasks(User):
    wait_time = between(1, 5)
        
    def on_start(self):
        print(f"Starting user with options: {self.environment.parsed_options}")
        self.user_data = {
            "token_native": self.environment.parsed_options.token_native,
            "token_underlying": self.environment.parsed_options.token_underlying,
            "num": self.environment.parsed_options.user_nums.pop(),
            "partner": False
        }
        self.all_tasks = self.environment.parsed_options.tasks
        self.log_steps = self.environment.parsed_options.log_steps

        # user attributes
        self.informer = Informer(**self.user_data)
        self.token_underlying = self.informer.token_underlying
        self.token_native = self.informer.token_native
        self.token_fasset = self.informer.token_fasset
        self.underlying_data = self.informer.underlying_data
        self.native_data = self.informer.native_data
        self.indexer_api_key = self.informer.indexer_api_key
        self.logger = self.informer.logger

        # logic
        self.ca = CoreActions(self.user_data)
        self.ca_partner = CoreActions({**self.user_data, "partner": True})
        self.lot_size = AssetManager("", "", self.token_underlying).lot_size()
        self.update_state()
        self.update_tasks()
        print(f"State on start: {self.state}")
        print(f"All tasks: {self.all_tasks}")
        print(f"All tasks: {self.tasks}")

    def update_state(self):
        self.balances = None # self.ca.get_balances()
        self.mint_status = self.ca.get_mint_status()
        self.redeem_status = self.ca.get_redemption_status()
        self.pools = self.ca.get_pools()
        self.pool_holdings = self.ca.get_pool_holdings()
        self.state = {
            "balances": self.balances,
            "mint_status": self.mint_status,
            "redeem_status": self.redeem_status,
            "pools": self.pools,
            "pool_holdings": self.pool_holdings
        }

    def update_tasks(self):
        self.tasks = [
            getattr(self, task_name)
            for task_name in self.all_tasks
            if getattr(conditions, f"can_{task_name}")(
                user_data=self.user_data, 
                state=self.state
            )
        ]

    # @staticmethod
    # def task_wrapper(weight=1):
    #     """
    #     A custom wrapper that incorporates Locust's @task decorator
    #     and adds logic to call update_tasks after the task.
    #     """
    #     def decorator(func):
    #         @task(weight)
    #         @wraps(func)
    #         def wrapped_task(self):
    #             func(self)
    #             self.update_tasks()
    #         return wrapped_task
    #     return decorator
    
    @task
    def mint_lowest_fee_agent_random_amount(self, _):
        print("Executing task: mint_lowest_fee_agent_random_amount")
        try:
            max_possible_lots = min(
                max_lots(self.get_agents()), 
                self.balances[self.token_underlying] // self.lot_size
                , 1
            )
            lot_amount = random.randint(1, max_possible_lots)
            agents = []
            current_lowest_fee = None
            for agent in self.get_agents():
                if agent["max_lots"] * self.lot_size >= lot_amount:
                    if current_lowest_fee is None or agent["fee"] < current_lowest_fee:
                        agents = [agent["address"]]
                        current_lowest_fee = agent["fee"]
                    elif agent["fee"] == current_lowest_fee:
                        agents.append(agent["address"])
            agent = random.choice(agents)
            self.ca.mint(lot_amount, agent, self.log_steps)
        except Exception as e:
            self.logger.error(f"Error executing task: {e}")
            events.request.fire(
                    request_type="task", 
                    name="mint_lowest_fee_agent_random_amount", 
                    response_time=0, 
                    response_length=0, 
                    exception=Exception(f"Exception during task execution: {e}")
                )        
        finally:
            expected_state = self.state.copy()
            expected_state["balances"][self.token_underlying] -= lot_amount * self.lot_size
            expected_state["balances"][self.token_fasset] += lot_amount * self.lot_size
            self.update_state()
            if self.state == expected_state:
                events.request.fire(
                    request_type="task", 
                    name="mint_lowest_fee_agent_random_amount", 
                    response_time=0, 
                    response_length=0
                )
            else:
                events.request.fire(
                    request_type="task", 
                    name="mint_lowest_fee_agent_random_amount", 
                    response_time=0, 
                    response_length=0, 
                    exception=Exception(f"State mismatch after task execution.\nExpected: {expected_state}\nGot: {self.state}")
                )

