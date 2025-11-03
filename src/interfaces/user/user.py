from abc import ABC
from config.config_qa import log_folder, fasset_name
from src.utils.secrets import load_user_secrets
import logging

class User(ABC):
    def __init__(self, token_underlying, num=0, partner=False):

        # tokens
        self.token_native = "C2FLR"
        self.token_underlying = token_underlying
        self.token_fasset = fasset_name[token_underlying]
        if token_underlying not in ["testXRP"]:
            raise ValueError(f"Unsupported token_underlying: {token_underlying}")
        
        # secrets
        secrets = load_user_secrets(num, partner)
        self.native_data = secrets["user"]["native"]
        self.underlying_data = secrets["user"][token_underlying]
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
        