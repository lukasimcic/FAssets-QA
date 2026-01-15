from abc import ABC
import os
import requests
from telegram import Bot
import logging
from pathlib import Path
from typing import Literal
import toml
from src.utils.secrets import load_user_secrets
from src.utils.data_structures import TokenFasset, TokenNative, TokenUnderlying, UserData, UserNativeData, UserUnderlyingData
from src.flow.fee_tracker import FeeTracker

config = toml.load("config.toml")
log_folder = Path(config["folder"]["log"])
bot_level = config["bot"]["level"]

BOT_TOKEN = os.environ["BOT_TOKEN"]
BOT_CHANNEL_ID = int(os.environ["BOT_CHANNEL_ID"])


class User(ABC):
    def __init__(self, user_data: UserData, fee_tracker : FeeTracker = None):
        token_native, token_underlying, num, partner, funder = (
            user_data.token_native,
            user_data.token_underlying,
            user_data.num,
            user_data.partner,
            user_data.funder
        )
        self.num = num
        self.partner = partner
        self.funder = funder
        self.fee_tracker = fee_tracker

        # tokens
        self.token_native : TokenNative = token_native
        self.token_underlying : TokenUnderlying = token_underlying
        self.token_fasset : TokenFasset = TokenFasset.from_underlying(token_underlying)
        
        # secrets
        secrets = load_user_secrets(num, partner, funder)
        self.native_data = UserNativeData(**secrets["user"]["native"])
        self.underlying_data = UserUnderlyingData(**secrets["user"][token_underlying.name])
        self.indexer_api_key = secrets["apiKey"]["indexer"][0]
        
        # logger
        if not funder:
            user_name = f"user{'_partner' if partner else ''}_{num}"
            log_file = log_folder / user_name[:-2] / f"{user_name}.log"
        else:
            user_name = "funder"
            log_file = log_folder / f"{user_name}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.touch()
        self.logger = logging.getLogger(user_name)
        if not self.logger.hasHandlers():
            self.logger.setLevel(logging.INFO)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(file_handler)

    def _send_telegram_message(self, message, level):
        if BOT_TOKEN and BOT_CHANNEL_ID:
            user_snippet = "funder" if self.funder else f"user{'_partner' if self.partner else ''} {self.num}"
            message = f"{level.capitalize()} message for {user_snippet}: {message}"
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": BOT_CHANNEL_ID,
                "text": message
            }
            requests.post(url, data=data)

    def log_step(self, message: str, log_steps: bool = True, level: Literal["info", "warning", "error"] = "info") -> None:
        if log_steps:
            match level:
                case "info":
                    self.logger.info(message)
                    if bot_level in ["info"]:
                        self._send_telegram_message(message, level)
                case "warning":
                    self.logger.warning(message)
                    if bot_level in ["info", "warning"]:
                        self._send_telegram_message(message, level)
                case "error":
                    self.logger.error(message)
                    if bot_level in ["info", "warning", "error"]:
                        self._send_telegram_message(message, level)
        