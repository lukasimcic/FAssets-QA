from utils.user_bot import UserBot
from utils.config import *

executor = UserBot(token_fasset)

pools = executor.get_pools()
pool_holdings = executor.get_pool_holdings()
print(pools)
print(pool_holdings)