
from config import *
from analizer.analize import Analizer
from ordersDispatcher.mainSeller import Seller
from ordersDispatcher.mainBuyer import Buyer
from ordersDispatcher.updateSellOrders import OrdersUpdater
from accounts import accounts

if __name__ == "__main__":
	need_start = list()
	# need_start.append("analize")
	need_start.append('updater')
	need_start.append('buyer')
	need_start.append("seller")
	need_start.append('balanceCalc')

	if 'analize' in need_start:
		analazer_proc = Analizer(5.0)
		analazer_proc.start()
		analazer_proc.join()

	if max(i in need_start for i in 
		('seller', 'buyer', 'updater')):
		accs = accounts.Accounts()
		accs.add(accounts.Account( *acc_data_1 ))
		accs.add(accounts.Account( *acc_data_2 ))
		accs.add(accounts.Account( *acc_data_3 ))
		accs.add(accounts.Account( *acc_data_4 ))

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
