from decimal import Decimal
import time
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from eth_account import Account
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.interfaces.network.native_networks.native_network import NativeBaseNetwork
from src.utils.data_structures import TokenNative


class C2FLR(NativeBaseNetwork):
    def __init__(self, address: str, private_key: str):
        super().__init__()
        self.token_native = TokenNative.C2FLR
        self.web3 = Web3(Web3.HTTPProvider(self.token_native.rpc_url))
        self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        self.address = address
        self.private_key = private_key

    def get_balance(self) -> Decimal:
        time.sleep(2) # avoid rate limiting
        balance_uba = self.web3.eth.get_balance(self.address)
        return self.token_native.from_uba(balance_uba)
    
    def send_transaction(self, to_address: str, amount: Decimal) -> dict:
        nonce = self.web3.eth.get_transaction_count(self.address)
        amount_wei = self.token_native.to_uba(amount)
        tx = {
            'nonce': nonce,
            'to': to_address,
            'value': amount_wei,
            'gas': 21000,
            'gasPrice': self.web3.eth.gas_price,
            'chainId': self.web3.eth.chain_id,
        }
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt

    def _get_current_block(self) -> int:
        return self.web3.eth.block_number
    
    def get_current_timestamp(self) -> int:
        current_block = self._get_current_block()
        block = self.web3.eth.get_block(current_block)
        return block.timestamp
    
    def generate_new_address(self) -> dict:
        acct = Account.create()
        secrets = {
            "address": acct.address,
            "private_key": acct.key.hex()
        }
        return secrets
    
    def request_funds(self) -> int:
        driver = webdriver.Chrome()  # or webdriver.Firefox() if you use Firefox

        try:
            driver.get(self.token_native.faucet_url)
            wait = WebDriverWait(driver, 10)
            input_field = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='Flare address']")
            ))
            input_field.clear()
            input_field.send_keys(self.address)

            # Button click cannot be automated due to CAPTCHA
            input("Please click the Request C2FLR button in the browser, then press Enter to continue...")

            time.sleep(1)
            success_message = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "p.mantine-focus-auto.m_b6d8b162.mantine-Text-root"))
            )[1]
            if not (success_message and success_message.text == f"Sent 100 C2FLR to {self.address}."):
                raise Exception(f"{'No output message.' if success_message is None else success_message.text}")

        finally:
            driver.quit()
        return 100