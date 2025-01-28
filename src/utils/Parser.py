
from typing import Any, List
from loguru import logger
import requests
import datetime
import time
import json
import os

class Parser:
    def __init__(self, with_retry: bool = True) -> None:
        self.last_page: None | str = None
        self.ses: requests.Session = requests.Session()
        self.with_retry = with_retry
        self.retry_time = 90
        self.retry_count = 3
        self.min_delay = 2 # in sec
        self.last_request_time = time.time()

        self._proxies = []
        self._pr_index = 0
        self._init_proxy()

    def _init_proxy(self):
        with open('proxies.txt', 'r') as file:
            l = file.read().split('\n')
            l = [i for i in l if i]

        if l:
            logger.info(f"Found {len(l)} proxies")
            self._proxies = [{"http":"http://"+proxy_s, "https":"http://"+proxy_s} for proxy_s in l]

    def ses_get(self, *args, **kwargs) -> requests.Response:
        cout = 0
        while cout < self.retry_count:
            if time.time() - self.last_request_time < 2:
                time.sleep(2 - time.time() + self.last_request_time)
            if not self._proxies:
                res = self.ses.get(*args, **kwargs)
            else:
                proxy = self._proxies[self._pr_index]
                res = self.ses.get(*args, **kwargs, proxies=proxy)
                self._pr_index += 1
                if self._pr_index >= len(self._proxies):
                    self._pr_index = 0
            self.last_request_time = time.time()
            if res.status_code == 200:
                return res
            time.sleep(self.retry_time)
            cout += 1

        return None

    def get_itemid_from_page(self, page: str) -> int | None:
        if page == None:
            return None
        x = page.find('Market_LoadOrderSpread(') + 24
        itemid = None
        try:
            itemid = int(page[x: x  + page[x:].find(' ')])
        except:
            pass 
        finally:
            return itemid
        
    def get_item_page(self, hash_name: str, appid: int | str = 252490) -> str | None:
        res = self.ses_get(f'https://steamcommunity.com/market/listings/{appid}/{hash_name}')
        if res.status_code != 200:
            self.last_page = res.text
            return None
        self.last_page = res.text
        return res.text
    
    def get_item_histogram(self, itemid: int) -> Any | None:
        res = self.ses_get(f'https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={itemid}')
        
        if res == None:
            return None
        if res.status_code != 200:
            return None
        
        return res.json()
    
    def get_history(self, page: str) -> List:
        start = page.find('var line1=')
        raw_history = json.loads(page[start + 10 : start + page[start:].find(']]') + 2]) # 10 - 'var line1=' size

        for i, el in enumerate(raw_history):
            raw_history[i][0] = datetime.datetime.strptime(el[0][:14], '%b %d %Y %H') # Feb 18 2016 01: +0

        history = raw_history

        return (history)