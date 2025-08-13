from utils.user_bot import UserBot
from utils.config import *

executor = UserBot(token_fasset)

executor.exit_pool("FCPT-TXRP-BIFROST", print_result=True, timeout=None)
pool_holdings = executor.withdraw_pool_fees(print_result=True, timeout=None)

print(pool_holdings)
