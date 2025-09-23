import subprocess
from src.utils.config import user_secrets_files, user_partner_secrets_files, log_path, project_path
import re
from contextlib import suppress
import logging
import json

class UserBot:
    """
    A class to interact with the user bot command line interface.
    It provides methods to execute commands and parse their output.
    """
    def __init__(self, token, num=0, partner=False, config=None, timeout=None):
        self.token = token
        self.timeout = timeout

        if not partner:
            secrets_file = user_secrets_files[num]
        else:
            secrets_file = user_partner_secrets_files[num]
        config_snippet = f"-c {config}" if config else ""
        self.command_prefix = f"yarn user-bot -s {secrets_file} {config_snippet} -f {token} "
        
        if not partner:
            log_file = log_path / "user-bots" / f"user-bot-{num}.log"
            self.logger = logging.getLogger(f"user-bot-{num}")
        else:
            log_file = log_path / "user-partner-bots" / f"user-partner-bot-{num}.log"
            self.logger = logging.getLogger(f"user-partner-bot-{num}")
        self.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)

        with open(secrets_file) as f:
            secrets = json.load(f)
            self.native_address = secrets["user"]["native"]["address"]
            self.native_private_key = secrets["user"]["native"]["private_key"]

    def _execute(self, command, log_steps):
        self.logger.info(f"Executing command: {command}")
        full_command = self.command_prefix + command
        p = subprocess.Popen(
            full_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=project_path,
            restore_signals=False,
            start_new_session=True,
            text=True,
        )
        lines = []
        try:
            for line in p.stdout:
                line = line.strip()
                lines.append(line)
                if log_steps:
                    self.logger.info(line)
            p.wait(timeout=self.timeout)
        except Exception as e:
            self.logger.error(f"Error while executing command:\n{e}")
            return lines
        self.logger.info(f"Command finished.")
        return lines

    def help(self, log_steps=False):
        """
        Returns the help message for the user bot.
        """
        return self._execute("help", log_steps)

    # Info commands

    def get_balances(self, log_steps=False):
        """
        Returns the balance of the user bot.
        """
        output = self._execute("balances", log_steps)
        balances = {}
        for line in output:
            amount, token = line.split(":")[1].strip().split(" ")
            balances[token] = float(amount)
        return balances

    def get_agents(self, log_steps=False):
        """
        Returns a list of parsed agent dicts.
        Each dict contains the agent's address, max_lots and fee.
        """
        output = self._execute("agents", log_steps)
        agents = []
        for line in output[1:]:  # Skip the header line
            try:
                address, max_lots, fee = line.split()
                agents.append(
                    {
                        "address": address,
                        "max_lots": int(max_lots),
                        "fee": float(fee.strip("%")),
                    }
                )
            except Exception as e:
                self.logger.error(f"Error parsing agent line '{line}': {e}")
        return agents

    def get_agent_info(self, agent, log_steps=False):
        """
        Returns a list of parsed agent info dicts.
        Each dict contains the agent's address, total_lots, total_minted, total_redeemed, total_fees and status.
        """
        output = self._execute(f"agentInfo {agent}", log_steps)
        data = {}
        for line in output:
            line = line.strip()
            if not line.endswith(':') and ':' in line:
                key, value = line.split(':', 1)
                key, value = key.strip(), value.strip()
                with suppress(ValueError):
                    value = float(value)
                data[key] = value
        return data

    def get_pools(self, log_steps=False):
        """
        Returns a list of pools available.
        Each pool is represented as a dictionary with keys like 'Pool address', 'Token symbol' and other pool data.
        """
        output = self._execute("pools", log_steps)
        pools = []
        header = re.split(r"\s{2,}", output[0].strip())
        for line in output[1:]:
            data = line.split()
            pool = {}
            for i, value in enumerate(data):
                with suppress(ValueError):
                    value = float(value)
                pool[header[i]] = value
            pools.append(pool)
        return pools

    def get_pool_holdings(self, log_steps=False):
        """
        Returns a list of pool holdings.
        Each holding is represented as a dictionary with keys 'Pool address', 'Token symbol', 'Pool tokens'.
        """
        output = self._execute("poolHoldings", log_steps)
        holdings = []
        header = re.split(r"\s{2,}", output[0].strip())
        for line in output[1:]:
            data = line.split()
            holding = {}
            for i, value in enumerate(data):
                with suppress(ValueError):
                    value = float(value)
                holding[header[i]] = value
            holdings.append(holding)
        return holdings

    # Mint and redeem actions

    def mint(self, amount, agent=None, log_steps=False):
        """
        Mints the specified amount from agent if it is provided.
        Otherwise the agent with lowest fee that has the capacity for minting enough lots is chosen.
        The minting will not be automatically split between agents.
        """
        command = f"mint {f'-a {agent}' if agent else ''} {amount}"
        return self._execute(command, log_steps)

    def redeem(self, amount, log_steps=False):
        """
        Redeems the specified amount.
        """
        command = f"redeem {amount}"
        return self._execute(command, log_steps)

    def execute_mint(self, mint_id, log_steps=False):
        """
        Executes minting with the specified id.
        """
        command = f"mintExecute {mint_id}"
        return self._execute(command, log_steps)

    def redeem_default(self, redemption_id, log_steps=False):
        """
        Redeems the default redemption with the specified id.
        """
        command = f"redemptionDefault {redemption_id}"
        return self._execute(command, log_steps)

    def get_mint_status(self, log_steps=False):
        """
        Returns a dictionary describing mint status of the user bot.
        """
        output = self._execute("mintStatus", log_steps)
        mint_status = {"EXPIRED": [], "PENDING": []}
        for line in output:
            if "  " in line:
                mint_id, status = line.split("  ", 1)
                if status in mint_status.keys():
                    mint_status[status] = mint_status[status] + [mint_id]
        return mint_status

    def get_redemption_status(self, log_steps=False):
        """
        Returns a dictionary describing remeption status of the user bot.
        """
        output = self._execute("redemptionStatus", log_steps)
        redemption_status = {"PENDING": [], "SUCCESS": [], "DEFAULT": [], "EXPIRED": []}
        for line in output:
            if "  " in line:
                redemption_id, status = line.split("  ", 1)
                if status in redemption_status.keys():
                    redemption_status[status] = redemption_status[status] + [
                        int(redemption_id.strip())
                    ]
        return redemption_status

    # Pool actions

    def enter_pool(self, pool_id, amount, log_steps=False):
        """
        Enters the specified pool with the given amount.
        """
        command = f"enterPool {pool_id} {amount}"
        return self._execute(command, log_steps)

    def exit_pool(self, pool_id, amount=None, log_steps=False):
        """
        Exits the specified pool with the given amount.
        If the amount is not specified, it exits the entire pool.
        """
        command = f"exitPool {pool_id} {amount if amount else 'all'}"
        return self._execute(command, log_steps)

    def withdraw_pool_fees(self, pool_id, log_steps=False):
        """
        Withdraws the fees from the specified pool.
        """
        command = f"withdrawPoolFees {pool_id}"
        return self._execute(command, log_steps)