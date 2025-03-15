
import time
import json
from multiprocessing import Process
from typing import List, Any
from loguru import logger
from accounts import accounts
from utils.Parser import Parser
from models.Table import ItemsBase
from steampy.models import GameOptions
from random import random
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import create_engine

class Seller(Process):
	'''
	Отвечает только за выставление предметов на продажу из всех инвентарей
	'''
	def __init__(self, accs: accounts.Accounts):
		super().__init__()
		self._accounts: List[accounts.Account] = accs.get_accounts()
		self._want_sell_table = {} # TODO name: wandRecive(per one), ADD want sell Table
		self._parser: Parser = Parser(use_proxy=False)
		self._db_session: None | Session = None

		# self.update_want_sell_table()

	def update_want_sell_table(self):
		# TODO create db table
		with open("seller/wantSell.json", "r") as file:
			try:
				self._want_sell_table = json.load(file)
				logger.success(f"Loaded want sell table( len: {len(self._want_sell_table)} )")
			except Exception as e:
				logger.error(f"On update want sell table {e}")

	def get_item_from_table(self, hash_name: str, appid: str) -> ItemsBase | None:
		item = self._db_session.query(ItemsBase).filter(
			ItemsBase.hash_name == hash_name,
			ItemsBase.appid == appid
		).first()

		return item

	def sell_markable_items(self, game: GameOptions = GameOptions.RUST):
		all_sell_send = 0
		sell_prices_updated = {}
		for acc in self._accounts:
			if not acc._steam_client.was_login_executed:
				continue;

			inventory = acc._steam_client.get_my_inventory(game)
			item_ids = list(inventory.keys())

			logger.info(f"Start sell {game.app_id} items on {acc.username} ")
			for item_id in item_ids:
				if inventory[item_id]['marketable'] != 1:
					continue
				hash_name = inventory[item_id]['market_hash_name']
				if "''" in hash_name:
					logger.info(f"Item skip {hash_name}")
					continue
				table_sell_price = self.get_item_from_table(hash_name, game.app_id)
				if table_sell_price:
					sell_price = int(table_sell_price.sell_price * 87)
				else:
					if hash_name not in sell_prices_updated:
						logger.info(f"Try get price: {hash_name}")
						self._parser.get_item_page(hash_name, game.app_id)
						if not self._parser.last_page:
							continue
						itemId = self._parser.get_itemid_from_page(self._parser.last_page)
						histogram = self._parser.get_item_histogram(itemId, hash_name, game.app_id)
						if not histogram:
							continue
						sell_price = round(float(histogram['sell_order_graph'][0][0]) * 87)
						sell_prices_updated[hash_name] = sell_price
					else:
						sell_price = sell_prices_updated[hash_name]

				if sell_price < 10:
					raise ValueError(f'Sell price is {sell_price}')
				
				all_sell_send += sell_price * int(inventory[item_id]['amount'])
				sell_price = str(sell_price)

				tryys = 3
				s = False
				while not s:
					sell_response = acc._steam_client.market.create_sell_order(item_id, game, sell_price, int(inventory[item_id]['amount']))
					s = sell_response['success']
					tryys -= 1
					time.sleep(3)

				if (sell_response['success']):
					logger.info(f"Sell {hash_name} recive {int(sell_price)/100}$")
				else:
					logger.error(f"{sell_response}\n{item_id} {game.app_id} {sell_price} {int(inventory[item_id]['amount'])}")

				time.sleep(2 + random())
			time.sleep(2 + random())
		logger.info(f"All sells {all_sell_send/100} $")

	def db_connect(self):
		engine = create_engine("sqlite:///database/market.db")
		Session = sessionmaker()
		Session.configure(bind=engine)
		self._db_session = Session()

	def run(self):
		self.db_connect()
		self.sell_markable_items(GameOptions.RUST)
		self.sell_markable_items(GameOptions.TF2)
		self._db_session.close()