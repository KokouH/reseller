from config import *
from typing import List
import time
from loguru import logger
from steampy.client import SteamClient

class Account:
    def __init__(
        self,
        api_key: str,
        username: str = None,
        password: str = None,
        steam_guard: str = None,
        login_cookies: dict = None,
        proxies: dict = None
    ) -> None:
        self.api_key = api_key
        self.username = username
        self.password = password
        self.steam_guard = steam_guard
        self.login_cookies = login_cookies
        self.proxies = proxies
        self.balance = 0.0
        self.max_risk = 0.0
        self.buy_orders_sum = 0.0
        self.sell_listings = None

        logger.info(f'Try login {username}')
        self._steam_client = SteamClient(api_key, username, password, steam_guard, proxies=proxies)
        self._steam_client.login()
        assert self._steam_client.was_login_executed
        logger.success(f"Login success")        

    def _update_balance(self):
        self.balance = float(self._steam_client.get_wallet_balance())

class Accounts:
    def __init__(self):
        self._accounts: Account = list()

    def add(self, account: Account):
        if not isinstance(account, Account):
            raise TypeError(f"Can add only Account type, not: {type(account)}")
        self._accounts.append(account)

    def get_accounts(self) -> List[Account]:
        return self._accounts
    
    def update_balances(self) -> None:
        for acc in self._accounts:
            acc._update_balance()
            time.sleep(2)

