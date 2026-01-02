from src.flow.flow import Flow
from src.actions import ACTION_BUNDLE_CLASSES
from src.utils.data_structures import UserData, TokenNative, TokenUnderlying
from src.flow.user_manager import UserManager
import threading

request_funds = True
user_nums = list(range(3))
token_native = TokenNative.C2FLR
token_underlying = TokenUnderlying.testXRP
cli = False

# names of classes of action bundles to include in the flow
# can customize actions for each thread here
all_actions = [
    [cls.__name__ for cls in ACTION_BUNDLE_CLASSES] 
    for _ in user_nums
    ]
mint_redeem_actions = [
    [
        "MintRandomAgentRandomAmount", 
        "MintLowestFeeAgentRandomAmount",
        "MintExecuteRandomMinting",
        "RedeemRandomAmount",
        "RedeemDefaultRandomRedemption"
    ] 
    for _ in user_nums
    ]
actions = all_actions

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
            total_time=60,
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
        t.start()
    for t in threads:
        t.join()
    um.collect_funds()