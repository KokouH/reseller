from multiprocessing import Process
import asyncio

from config import *
from analizer.analize import Analizer
from ordersDispatcher.mainSeller import Seller
from ordersDispatcher.mainBuyer import Buyer
from ordersDispatcher.updateOrders import OrdersUpdater
from accounts import accounts
from utils.TelegramBot import send_message

class BotMain(Process):
	def __init__(self, need_start):
		super().__init__()
		self._need_start = need_start
		
		
	def run(self):
		need_start = self._need_start

		if 'analize' in need_start:
			analazer_proc = Analizer(5.0)
			analazer_proc.start()
			analazer_proc.join()

		if max(i in need_start for i in 
			('seller', 'buyer', 'updater', 'balanceCalc')):
			accs = accounts.Accounts()
			accs.add(accounts.Account( *acc_data_1 ))
			accs.add(accounts.Account( *acc_data_2 ))
			accs.add(accounts.Account( *acc_data_3 ))
			accs.add(accounts.Account( *acc_data_4 ))
			asyncio.run(send_message("All accounts login"))

		if 'updater' in need_start:
			updater_proc = OrdersUpdater(accs)
			updater_proc.start()
			updater_proc.join()
			
		if 'seller' in need_start:
			seller_proc = Seller(accs)
			seller_proc.start()
			seller_proc.join()

		if 'buyer' in need_start:
			buyer_proc = Buyer(accs)
			buyer_proc.start()
			buyer_proc.join()

		if 'balanceCalc' in need_start:
			import balanceCalculate
			balanceCalculate.main(accs)