
import time
from random import random
from multiprocessing import Process
from typing import List
from loguru import logger
from accounts import accounts
from utils.Parser import Parser
from steampy.exceptions import ApiException
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

class OrdersUpdater(Process):
	'''
	Отвечает только за оредров перевыставление
	'''
	def __init__(self, accs: accounts.Accounts):
		super().__init__()
		accs.update_balances()
		self._accounts: List[accounts.Account] = accs.get_accounts()
		self._parser: Parser = Parser()
		self._session = None

	

	def run(self):
		engine = create_engine("sqlite:///database/market.db")
		Session = sessionmaker()
		Session.configure(bind=engine)
		self._session = Session()

		self.buy_order_update()
