from config.config_qa import log_folder, fasset_name
from src.utils.secrets import load_user_secrets
from src.utils.data_structures import TokenFasset, TokenNative, TokenUnderlying, UserData, UserNativeData, UserUnderlyingData
from src.utils.fee_tracker import FeeTracker
from abc import ABC
import logging



class User(ABC):
    def __init__(self, user_data: UserData, fee_tracker : FeeTracker = None):
        token_native, token_underlying, num, partner = (
            user_data.token_native,
            user_data.token_underlying,
            user_data.num,
            user_data.partner
        )
        self.fee_tracker = fee_tracker

        # tokens
        self.token_native : TokenNative = token_native
        self.token_underlying : TokenUnderlying = token_underlying
        self.token_fasset : TokenFasset = fasset_name[token_underlying]
        
        # secrets
        secrets = load_user_secrets(num, partner)
        self.native_data = UserNativeData(**secrets["user"]["native"])
        self.underlying_data = UserUnderlyingData(**secrets["user"][token_underlying])
        self.indexer_api_key = secrets["apiKey"]["indexer"][0]
        
        # logger
        user_name = f"user{'_partner' if partner else ''}_{num}"
        log_file = log_folder / user_name[:-2] / f"{user_name}.log"
        self.logger = logging.getLogger(user_name)
        if not self.logger.hasHandlers():
            self.logger.setLevel(logging.INFO)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(file_handler)

    def log_step(self, message, log_steps):
        if log_steps:
            self.logger.info(message)