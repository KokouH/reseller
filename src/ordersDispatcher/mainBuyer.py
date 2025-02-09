
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

class Buyer(Process):
	'''
	Отвечает только за выставление оредров на покупку
	'''
	def __init__(self, accs: accounts.Accounts):
		super().__init__()
		accs.update_balances()
		self._accounts: List[accounts.Account] = accs.get_accounts()
		self._all_balance = sum(acc.balance for acc in self._accounts)

	def buy_items_on_all(self, items: List[ItemsBase]):
		for acc in self._accounts:
			acc.max_risk = (acc.balance * 8) / len(items) # TODO old method risk distribute, UPDATE
			logger.info(f"Max risk {acc.max_risk} for {acc.username}")

		for percent, item in items:
			if item.buy_price < 0.1:
				continue
			for acc in self._accounts:
				try:
					responce = acc._steam_client.market.create_buy_order(
						item.hash_name,
						str(int(item.buy_price * 100)),
						int(acc.max_risk / item.buy_price + 1),
						GameOptions.TF2 if item.appid == "440" else GameOptions.RUST,
						Currency.USD
					)
				except ApiException as e:
					logger.critical(f"{acc._steam_client.username} is can't create order {item.hash_name}\n{e}")
					print(acc.max_risk, item.buy_price)
					for _ in range(100):
						time.sleep(random())
					if responce.get('success') == 25:
						self._accounts.remove(acc)
				
				time.sleep(random()*2 + 2)

			if not len(self._accounts):
				break;

			logger.info(f"Created orders {int(percent/len(items) * 100)}%: {item.hash_name}, {item.buy_price}$ per one")

	def buy_items_on_all_normal_speed(self, items: List[ItemsBase]):
		risk = self._all_balance * 8 / len(items)
		i = 0
		while i < len(self._accounts):
			if self._accounts[i].balance <= risk:
				logger.info(f"Remove account from circle: {self._accounts[i].username}")
				del(self._accounts[i])
			else:
				i += 1

		if not self._accounts:
			raise Exception(f"Can't create new buy orders, ")
		
		self._all_balance = sum(acc.balance for acc in self._accounts)
		risk = self._all_balance * 8 / len(items)
		logger.info(f"Balances: {self._all_balance}, risk: {risk}")
		acc_index = 0
		for item in items:
			buy_count = int(risk / item.buy_price)
			if not buy_count:
				buy_count = 1
			success = 0
			while not success:
				try:
					acc = self._accounts[acc_index]
					if (item.buy_price * buy_count + acc.buy_orders_sum >= acc.balance * 10):
						acc_index += 1
						acc = self._accounts[acc_index]
						logger.info(f"Change account to {acc.username}")
					responce = acc._steam_client.market.create_buy_order(
						item.hash_name,
						str(int(item.buy_price * 100)),
						buy_count,
						GameOptions(item.appid, '2'),
						Currency.USD
					)
					if (responce.get('success') == 1 # created
						or responce.get('success') == 29 # already exists
					):
						success = 1
						acc.buy_orders_sum += item.buy_price * buy_count
					else:
						logger.error(f"{acc._steam_client.username} is can't create order {item.hash_name}")
						if responce.get('success') != 16: # steam: Sorry! We had trouble
							for _ in range(130):
								time.sleep(random())
						time.sleep(random() * 3)
					
				except IndexError as e:
					logger.critical(f"{items.index(item) + 1} not created of {len(items)}")
					exit(-1)
				except Exception as e:
					logger.critical(e)
					exit(-1)

			logger.info(f"Created orders {int(items.index(item)/len(items) * 100)}%: {item.hash_name}, {item.buy_price}$ per one")
			time.sleep(random() * 2 + 2)

		logger.success("All buy orders created")

	def run(self):
		engine = create_engine("sqlite:///database/market.db")
		Session = sessionmaker()
		Session.configure(bind=engine)
		session = Session()

		f_items = session.query(ItemsBase).filter(
			ItemsBase.trend_30d >= .98,
			ItemsBase.trend_30d <= 1.3,
			ItemsBase.trend_7d >= .95,
			ItemsBase.sells_30d >= 80,
			ItemsBase.history_stable == True,
			ItemsBase.buy_price_deep <= 5,
			ItemsBase.buy_price >= .1,
			ItemsBase.sell_price_conf >= .2).all()

		self.buy_items_on_all_normal_speed(f_items)