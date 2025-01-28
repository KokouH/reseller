
from config import *
from analizer.analize import Analizer
from seller.mainSeller import Seller
from accounts import accounts

if __name__ == "__main__":
	need_start = list()
	need_start.append("analize")
	# need_start.append("seller")

	procs = list()

	# accs = accounts.Accounts()
	# accs.add(accounts.Account( *acc_data_1 ))
	# accs.add(accounts.Account( *acc_data_2 ))
	# accs.add(accounts.Account( *acc_data_3 ))
	# accs.add(accounts.Account( *acc_data_4 ))

	if 'seller' in need_start:
		seller_proc = Seller(accs)
		procs.append(seller_proc)

	if 'analize' in need_start:
		analazer_proc = Analizer()
		procs.append(analazer_proc)

	for pr in procs:
		pr.start()

	for pr in procs:
		pr.join()