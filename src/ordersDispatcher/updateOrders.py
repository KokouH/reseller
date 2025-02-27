
import time
from random import random
from multiprocessing import Process
from typing import List
from loguru import logger
from accounts import accounts
from utils.Parser import Parser
from models.Table import ItemsBase
from steampy.models import GameOptions, Currency
from steampy.exceptions import ApiException
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

class OrdersUpdater(Process):
	'''
	Отвечает только за перевыставление оредров
	'''
	def __init__(self, accs: accounts.Accounts):
		super().__init__()
		accs.update_balances()
		self._accounts: List[accounts.Account] = accs.get_accounts()
		self._parser: Parser = Parser()
		self._session = None

	def sell_order_update(self):
		if not self._session:
			logger.critical(f"Updater not connect to DB")

		for acc in self._accounts:
			try:
				logger.info(f"Start update orders on {acc.username}")
				acc.sell_listings = acc._steam_client.market.get_my_market_listings()['sell_listings']
				acc.sell_listings = list(acc.sell_listings.values())

				for sell_order in acc.sell_listings:
					hash_name = sell_order['description']['market_hash_name']
					appid = sell_order['description']['appid']
					sell_price = float(sell_order['buyer_pay'].replace('$', '').replace(' USD', '').replace(' each', ''))
					item = self._session.query(ItemsBase).filter(
						ItemsBase.hash_name == hash_name,
						ItemsBase.appid == appid,
						ItemsBase.sell_price != sell_price
					).first()
					if item:
						try:
							logger.info(f"Update sellOrder {hash_name}")
							acc._steam_client.market.cancel_sell_order(sell_order['listing_id'])
							time.sleep(random() * 2 + 2)
						except Exception as e:
							logger.error(f"Can't cancel order {sell_order}")
			except Exception as e:
				logger.error(f"Problem with {acc.username}\n{sell_order}\n{e}")
		logger.success(f"All sell orders updated")

	def buy_order_update(self):
		if not self._session:
			logger.critical(f"Updater not connect to DB")

		for acc in self._accounts:
			try:
				logger.info(f"Start update orders on {acc.username}")
				acc.sell_listings = acc._steam_client.market.get_my_market_listings()['buy_orders']
				acc.sell_listings = list(acc.sell_listings.values())

				for buy_order in acc.sell_listings:
					try:
						acc._steam_client.market.cancel_buy_order(buy_order['order_id'])
						logger.info(f"Update buyOrder {buy_order['item_name']}")
					except ApiException as e:
						pass
					time.sleep(random() * 2 + 2)
			except Exception as e:
				logger.error(f"Problem with {acc.username}\n{buy_order}\n{e}")
		logger.success(f"All buy orders updated")

	def run(self):
		engine = create_engine("sqlite:///database/market.db")
		Session = sessionmaker()
		Session.configure(bind=engine)
		self._session = Session()

		self.buy_order_update()
		self.sell_order_update()
