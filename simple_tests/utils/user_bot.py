import subprocess
from utils.config import *
import re
from contextlib import suppress


class UserBot:
    """
    A class to interact with the user bot command line interface.
    It provides methods to execute commands and parse their output.
    """
    def __init__(self, token):
        self.token = token
        self.command_prefix = f"yarn user-bot -f {token} "

    def _execute(self, command, print_result, timeout):
        full_command = self.command_prefix + command
        print("---")
        print(f"Executing command: {full_command}")
        p = subprocess.Popen(
            full_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=project_folder,
            restore_signals=False,
            start_new_session=True,
            text=True,
        )
        lines = []
        try:
            for line in p.stdout:
                line = line.strip()
                lines.append(line)
                if print_result:
                    print(line)
            p.wait(timeout=timeout)
        except Exception as e:
            print(f"Error executing command: {e}")
            return lines
        if not print_result:
            print(f"Command finished.")
        return lines

    def help(self, print_result=False, timeout=None):
        """
        Returns the help message for the user bot.
        """
        return self._execute("help", print_result, timeout)

    def get_balances(self, print_result=False, timeout=None):
        """
        Returns the balance of the user bot.
        """
        output = self._execute("balances", print_result, timeout)
        balances = {}
        for line in output:
            amount, token = line.split(":")[1].strip().split(" ")
            balances[token] = float(amount)
        return balances

    def get_agents(self, print_result=False, timeout=None):
        """
        Returns a list of parsed agent dicts.
        Each dict contains the agent's address, max_lots and fee.
        """
        output = self._execute("agents", print_result, timeout)
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
                print(f"Error parsing agent line '{line}': {e}")
        return agents

    # Mint and redeem actions

    def mint(self, amount, agent=None, print_result=False, timeout=None):
        """
        Mints the specified amount from agent if it is provided.
        Otherwise the agent with lowest fee that has the capacity for minting enough lots is chosen.
        The minting will not be automatically split between agents.
        """
        command = f"mint {f'-a {agent}' if agent else ''} {amount}"
        return self._execute(command, print_result, timeout)

    def redeem(self, amount, print_result=False, timeout=None):
        """
        Redeems the specified amount.
        """
        command = f"redeem {amount}"
        return self._execute(command, print_result, timeout)

    def execute_mint(self, mint_id, print_result=False, timeout=None):
        """
        Executes minting with the specified id.
        """
        command = f"mintExecute {mint_id}"
        return self._execute(command, print_result, timeout)

    def redeem_default(self, redemption_id, print_result=False, timeout=None):
        """
        Redeems the default redemption with the specified id.
        """
        command = f"redemptionDefault {redemption_id}"
        return self._execute(command, print_result, timeout)

    def get_mint_status(self, print_result=False, timeout=None):
        """
        Returns a dictionary describing mint status of the user bot.
        """
        output = self._execute("mintStatus", print_result, timeout)
        mint_status = {"EXPIRED": [], "PENDING": []}
        for line in output:
            if "  " in line:
                mint_id, status = line.split("  ", 1)
                if status in mint_status.keys():
                    mint_status[status] = mint_status[status] + [mint_id]
        return mint_status

    def get_redemption_status(self, print_result=False, timeout=None):
        """
        Returns a dictionary describing remeption status of the user bot.
        """
        output = self._execute("redemptionStatus", print_result, timeout)
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

    def get_pools(self, print_result=False, timeout=None):
        """
        Returns a list of pools available.
        Each pool is represented as a dictionary with keys like 'Pool address', 'Token symbol' and other pool data.
        """
        output = self._execute("pools", print_result, timeout)
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

    def get_pool_holdings(self, print_result=False, timeout=None):
        """
        Returns a list of pool holdings.
        Each holding is represented as a dictionary with keys 'Pool address', 'Token symbol', 'Pool tokens'.
        """
        output = self._execute("poolHoldings", print_result, timeout)
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

    def enter_pool(self, pool_id, amount, print_result=False, timeout=None):
        """
        Enters the specified pool with the given amount.
        """
        command = f"enterPool {pool_id} {amount}"
        return self._execute(command, print_result, timeout)

    def exit_pool(self, pool_id, amount=None, print_result=False, timeout=None):
        """
        Exits the specified pool with the given amount.
        If the amount is not specified, it exits the entire pool.
        """
        command = f"exitPool {pool_id} {amount if amount else 'all'}"
        return self._execute(command, print_result, timeout)

    def withdraw_pool_fees(self, pool_id, print_result=False, timeout=None):
        """
        Withdraws the fees from the specified pool.
        """
        command = f"withdrawPoolFees {pool_id}"
        return self._execute(command, print_result, timeout)