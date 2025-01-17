from config import *
from typing import List
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
        self.balane = 0.0

        self._steam_client = SteamClient(api_key, username, password, steam_guard, login_cookies, proxies)

    def _update_balance(self):
        self.balane = float(self._steam_client.get_wallet_balance())

class Accounts:
    def __init__(self):
        self._accounts: Account = list()

    def add(self, account: Account):
        if type(account) != type(Account()):
            raise TypeError(f"Can add only Account type, not: {type(account)}")
        self._accounts.append(account)

    def get_accounts(self) -> List[Account]:
        return self._accounts
    
    def update_balances(self):
        for acc in self._acoounts:
            acc._update_balance()

