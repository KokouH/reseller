
import time
import json
from multiprocessing import Process
from typing import List
from loguru import logger
from accounts import accounts
from utils.Parser import Parser
from steampy.models import GameOptions

class Seller(Process):
    '''
    Отвечает только за выставление предметов на продажу из всех инвентарей
    '''
    def __init__(self, accs: accounts.Accounts):
        super().__init__()
        self._accounts: List[accounts.Account] = accs.get_accounts()
        self._want_sell_table = {} # TODO name: wandRecive(per one), ADD want sell Table
        self._parser: Parser = Parser()

        self.update_want_sell_table()

    def update_want_sell_table(self):
        # TODO create db table
        with open("seller/wantSell.json", "r") as file:
            try:
                self._want_sell_table = json.load(file)
                logger.success(f"Loaded want sell table( len: {len(self._want_sell_table)} )")
            except Exception as e:
                logger.error(f"On update want sell table {e}")

    def sell_markable_items(self, game: GameOptions = GameOptions.RUST):
        all_sell_send = 0
        sell_prices_updated = {}
        for acc in self._accounts:
            logger.info(f"Start sell intems on {acc.username}")
            if not acc._steam_client.was_login_executed:
                continue;

            inventory = acc._steam_client.get_my_inventory(game)
            item_ids = list(inventory.keys())

            for item_id in item_ids:
                if inventory[item_id]['marketable'] != 1:
                    continue
                hash_name = inventory[item_id]['name']
                sell_price_table = round(self._want_sell_table[hash_name] * 87) if hash_name in self._want_sell_table else 0
                if hash_name not in sell_prices_updated:
                    logger.info(f"Try get price: {hash_name}")
                    self._parser.get_item_page(hash_name)
                    itemId = self._parser.get_itemid_from_page(self._parser.last_page)
                    histogram = self._parser.get_item_histogram(itemId)
                    if self._parser.last_page is None or histogram is None:
                        continue
                    sell_price_now = round(float(histogram['sell_order_graph'][0][0]) * 87)
                    sell_prices_updated[hash_name] = sell_price_now
                else:
                    sell_price_now = sell_prices_updated[hash_name]

                sell_price = sell_price_table if sell_price_table > sell_price_now else sell_price_now

                if sell_price < 10:
                    raise ValueError(f'Sell price is {sell_price}')
                
                all_sell_send += sell_price * int(inventory[item_id]['amount'])
                sell_price = str(sell_price)
                sell_response = acc._steam_client.market.create_sell_order(item_id, game, sell_price, int(inventory[item_id]['amount']))

                if (sell_response['success']):
                    logger.info(f"Sell {hash_name} recive {int(sell_price)/100}$")
                else:
                    logger.error(sell_response)
                    exit(-1)

                time.sleep(2)
        logger.info(f"All sells {all_sell_send/100} $")

    def run(self):
        self.sell_markable_items()