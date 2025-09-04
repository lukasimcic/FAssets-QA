from utils.user_bot import UserBot
from utils.config import *

executor = UserBot(token_underlying)
result = executor.help()

for line in result:
    print(line)
