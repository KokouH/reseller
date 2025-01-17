
import json
import sqlite3
import time

from models import Table
from models.Table import Items
from utils.Parser import Parser
from utils import AnalizeFuncs

from typing import List, Any
from loguru import logger
from multiprocessing import Process
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class AnalItem:
	def __init__(self, hash_name: str, appid: str):
		self.hash_name: str = hash_name
		self.appid: str | int = appid

class Analizer(Process):
	def __init__(self, wanted_profit:float = 4):
		super().__init__()
		self._analize_items: List[AnalItem] = list()
		self._db_session: None | Any = None
		
		self._wanted_profit = wanted_profit

	def load_items(self):
		appid = '252490' # Rust
		with open("analizer/item_names/rust.json", "r") as file:
			for item_name in json.load(file):
				self._analize_items.append( AnalItem(item_name, appid) )

		appid = '440' # Tf2
		with open("analizer/item_names/tf2.json", "r") as file:
			for item_name in json.load(file):
				self._analize_items.append( AnalItem(item_name, appid) )
	
	def start_analize(self):
		parser = Parser()
		item_steam_ids = dict()
		while 1:
			for item in self._analize_items:
				try:
					logger.info(f"Analize item: {item.hash_name}")
					parser.get_item_page(item.hash_name, item.appid)
					if item.hash_name not in item_steam_ids:
						steamid = parser.get_itemid_from_page(parser.last_page)
					else:
						steamid = item_steam_ids[item.hash_name]
					histogram = parser.get_item_histogram(steamid)
					if (parser.last_page == None 
						or steamid == None
						or histogram == None
					):
						time.sleep(90)
						continue
					history = parser.get_history(parser.last_page)

					t_item = Items()
					t_item.hash_name = item.hash_name
					t_item.appid = item.appid
					t_item.steamid = steamid
					t_item.count_buy = AnalizeFuncs.get_sells_n_days(history, 2)
					t_item.sell_price = histogram['sell_order_graph'][0][0]
					t_item.buy_price = t_item.sell_price * .87 * (1 - self._wanted_profit /  100)
					t_item.trend_7d = AnalizeFuncs.get_trend_week(history)
					t_item.trend_30d = AnalizeFuncs.get_month_sells(history)
					t_item.sells_7d = AnalizeFuncs.get_week_sells(history)
					t_item.sells_30d = AnalizeFuncs.get_month_sells(history)
					t_item.sell_price_conf = AnalizeFuncs.get_sell_in_history(history, t_item.sell_price)
					t_item.buy_price_deep = AnalizeFuncs.get_deep_in_cup(histogram, t_item.sells_30d, t_item.buy_price)
					t_item.history_stable = AnalizeFuncs.get_history_stable(history)

					self._db_session.add(t_item)
					self._db_session.commit()
					logger.info(f"Add item {item.hash_name}")
				except Exception as e:
					logger.error(e)

	def db_connect(self):
		engine = create_engine("sqlite:///database/market.db")
		Table.Base.metadata.create_all(engine)
		Session = sessionmaker()
		Session.configure(bind=engine)
		self._db_session = Session()

	def run(self):
		self.load_items()
		self.db_connect()
		self.start_analize()

if __name__ == "__main__":
	anal = Analizer(4)
	anal.start()
	anal.join()