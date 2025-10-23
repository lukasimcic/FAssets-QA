from src.flow.flow_cli import FlowCli
from src.flow.flow_manual import FlowManual
from src.utils.config import NUM_USER_BOTS
from src.actions import ACTION_BUNDLE_CLASSES
import threading

token_underlying = "testXRP"

# names of classes of action bundles to include in the flow
# can customize actions for each thread here
all_actions = [
    [cls.__name__ for cls in ACTION_BUNDLE_CLASSES] 
    for _ in range(NUM_USER_BOTS)
    ]
actions = [
    ["MintRandomAgentRandomAmount", "MintLowestFeeAgentRandomAmount"] 
    for _ in range(NUM_USER_BOTS)
    ]

def make_threads(actions):
    threads = []
    for i in range(NUM_USER_BOTS):
        flow = FlowManual(
            token_underlying=token_underlying,
            actions=actions[i],
            num=i,
            total_time=30,
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