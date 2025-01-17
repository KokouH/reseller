
import time
import multiprocessing
from src.accounts import accounts
from src.utils import Parser
from steampy.models import GameOptions

class Seller:
    '''
    Отвечает только за выставление предметов на продажу из всех инвентарей
    '''
    def __init__(self, accounts: accounts.Accounts):
        self._accounts = accounts.get_accounts()
        self._want_sell_table = {} # name: wandRecive(per one)
        self._parser: Parser = Parser()

    def sell_markable_items(self, game: GameOptions = GameOptions.RUST):
        sell_prices_updated = {}
        for acc in self._accounts:
            if not acc._steam_client.was_login_executed:
                continue;

            inventory = acc._steam_client.get_my_inventory(game)
            item_ids = list(inventory.keys())

            for item_id in item_ids:
                if inventory[item_id]['marketable'] != 1:
                    continue

                sell_price_table = round(self._want_sell_table[inventory[item_id]['name']] * 87)
                if inventory[item_id]['name'] not in sell_prices_updated:
                    print(f"Try get price: {inventory[item_id]['name']}")
                    self._parser.get_item_page(inventory[item_id]['name'])
                    itemId = self._parser.get_itemid_from_page(self._parser.last_page)
                    histogram = self._parser.get_item_histogram(itemId)
                    if self._parser.last_page is None or histogram is None:
                        continue
                    sell_price_now = round(float(histogram['sell_order_graph'][0][0]) * 87)
                    sell_prices_updated[inventory[item_id]['name']] = sell_price_now
                else:
                    sell_price_now = sell_prices_updated[inventory[item_id]['name']]

                sell_price = sell_price_table if sell_price_table > sell_price_now else sell_price_now

                if sell_price < 10:
                    raise ValueError(f'Sell price is {sell_price}')
                sell_price = str(sell_price)
                sell_response = acc._steam_client.market.create_sell_order(item_id, game, sell_price)

                if (sell_response['success']):
                    print(f"Sell {inventory[item_id]['name']} recive {int(sell_price)/100}$")
                else:
                    print(sell_response)
                    exit(-1)

                time.sleep(2)
    print("All sell's created")