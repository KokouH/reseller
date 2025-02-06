
import json
import time

from models import Table
from models.Table import ItemsBase
from utils.Parser import Parser
from utils import AnalizeFuncs

from typing import List, Any
from loguru import logger
from multiprocessing import Process
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker

class AnalItem:
	def __init__(self, hash_name: str, appid: str):
		self.hash_name: str = hash_name
		self.appid: str | int = appid

class Analizer(Process):
	def __init__(self, wanted_profit:float = 6):
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
					steamid = parser.get_itemid_from_page(parser.last_page)
					histogram = parser.get_item_histogram(steamid, item.hash_name, item.appid)
					if (parser.last_page == None 
						or steamid == None
						or histogram == None
					):
						logger.info(f"Item skiped: {item.hash_name}")
						continue
					history = parser.get_history(parser.last_page)

					t_item = ItemsBase()
					t_item.hash_name = item.hash_name
					t_item.appid = item.appid
					t_item.steamid = steamid
					t_item.count_buy = AnalizeFuncs.get_sells_n_days(history, 2)
					t_item.sell_price = AnalizeFuncs.get_reference_price(history)
					t_item.buy_price = t_item.sell_price * .87 * (1 - self._wanted_profit /  100)
					t_item.trend_7d = AnalizeFuncs.get_trend_week(history)
					t_item.trend_30d = AnalizeFuncs.get_trend_month(history)
					t_item.sells_7d = AnalizeFuncs.get_week_sells(history)
					t_item.sells_30d = AnalizeFuncs.get_month_sells(history)
					t_item.sell_price_conf = AnalizeFuncs.get_sell_in_history(history, t_item.sell_price)
					t_item.buy_price_deep = AnalizeFuncs.get_deep_in_cup(histogram, t_item.sells_30d, t_item.buy_price)
					t_item.history_stable = AnalizeFuncs.get_volatility(history) <= .2

					table_item = self._db_session.query(ItemsBase).where(ItemsBase.hash_name == item.hash_name).first()
					if table_item:
						update_dict = dict(t_item.__dict__)
						del(update_dict['_sa_instance_state'])
						self._db_session.query(ItemsBase).filter(ItemsBase.hash_name == item.hash_name).update(update_dict)
					else:
						self._db_session.add(t_item)

					try:
						self._db_session.commit()
					except Exception as e:
						self._db_session.rollback()
						logger.critical(f"Commit to db")
						exit(-1)

					logger.info(f"Add item {item.hash_name}")
				except Exception as e:
					logger.error(e)

	def db_connect(self):
		engine = create_engine("sqlite:///database/market.db")
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