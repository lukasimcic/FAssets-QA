from src.utils.config import user_secrets_files, user_partner_secrets_files, log_path
import logging
import json

class User():
    def __init__(self, token_underlying, num=0, partner=False):
        if not partner:
            self.secrets_file = user_secrets_files[num]
            log_file = log_path / "user-bots" / f"user-bot-{num}.log"
            self.logger = logging.getLogger(f"user-bot-{num}")
        else:
            self.secrets_file = user_partner_secrets_files[num]
            log_file = log_path / "user-partner-bots" / f"user-partner-bot-{num}.log"
            self.logger = logging.getLogger(f"user-partner-bot-{num}")
        
        if not self.logger.hasHandlers():
            self.logger.setLevel(logging.INFO)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(file_handler)

        self.token_native = "C2FLR"
        match token_underlying:
            case "testXRP":
                self.token_underlying = "testXRP"
                self.token_fasset = "FTestXRP"
            case _:
                raise ValueError(f"Unsupported token_underlying: {token_underlying}")

        with open(self.secrets_file) as f:
            secrets = json.load(f)
            self.native_data = secrets["user"]["native"]
            self.underlying_data = secrets["user"][token_underlying]
            self.indexer_api_key = secrets["apiKey"]["indexer"][0]

    def log_step(self, message, log_steps):
        if log_steps:
            self.logger.info(message)
        