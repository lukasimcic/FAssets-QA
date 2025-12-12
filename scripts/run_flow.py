from src.flow import Flow
from src.actions import ACTION_BUNDLE_CLASSES
from src.utils.data_structures import UserData, TokenNative, TokenUnderlying
import threading


num_user_bots = 1
token_native = TokenNative.C2FLR
token_underlying = TokenUnderlying.testXRP
cli = False

# names of classes of action bundles to include in the flow
# can customize actions for each thread here
all_actions = [
    [cls.__name__ for cls in ACTION_BUNDLE_CLASSES] 
    for _ in range(num_user_bots)
    ]
mint_redeem_actions = [
    [
        "MintRandomAgentRandomAmount", 
        "MintLowestFeeAgentRandomAmount",
        "MintExecuteRandomMinting",
        "RedeemRandomAmount",
        "RedeemDefaultRandomRedemption"
    ] 
    for _ in range(num_user_bots)
    ]
actions = [
    [
        "MintExecuteRandomMinting",
        "RedeemDefaultRandomRedemption"

    ]
    for _ in range(num_user_bots)
    ]

def make_threads(actions):
    threads = []
    for i in range(num_user_bots):
        flow = Flow(
            UserData(
                token_native=token_native,
                token_underlying=token_underlying,
                num=i
            ),
            actions=actions[i],
            cli=cli,
            total_time=100,
            time_wait=5
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