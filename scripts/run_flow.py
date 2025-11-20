from src.flow.flow_cli import FlowCli
from src.flow.flow_manual import FlowManual
from src.flow.flow_actions import ACTION_BUNDLE_CLASSES
import threading

num_user_bots = 2
token_underlying = "testXRP"
flow_class = FlowManual

# names of classes of action bundles to include in the flow
# can customize actions for each thread here
all_actions = [
    [cls.__name__ for cls in ACTION_BUNDLE_CLASSES] 
    for _ in range(num_user_bots)
    ]
actions = [
    [
        "MintRandomAgentRandomAmount", 
        "MintLowestFeeAgentRandomAmount",
        "MintExecuteRandomMinting",
        "RedeemRandomAmount",
        "RedeemDefaultRandomRedemption"
    ] 
    for _ in range(num_user_bots)
    ]

def make_threads(actions):
    threads = []
    for i in range(num_user_bots):
        flow = flow_class(
            token_underlying=token_underlying,
            actions=actions[i],
            num=i,
            total_time=300,
            time_wait=10
            )
        t = threading.Thread(target=flow.run)
        threads.append(t)
    return threads

if __name__ == "__main__":
    threads = make_threads(actions)
    for t in threads:
        t.start()
    for t in threads:
        t.join()