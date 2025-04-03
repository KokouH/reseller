import os

from config import *
from analizer.analize import Analizer
from ordersDispatcher.mainSeller import Seller
from ordersDispatcher.mainBuyer import Buyer
from ordersDispatcher.updateOrders import OrdersUpdater
from accounts import accounts

from Bot import EndPoints
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler

def MainWithBot():
	application = Application.builder().token(TOKEN_TG).build()
	application.add_handler(CommandHandler("start", EndPoints.start))
	application.add_handler(CallbackQueryHandler(EndPoints.button))
	application.add_handler(MessageHandler(None, EndPoints.message_handler))
	application.run_polling(allowed_updates=Update.ALL_TYPES)

def Main(need_start):
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

if __name__ == "__main__":
	if not os.path.isdir('database'):
		os.mkdir('database')

	if not USE_BOT:
		need_start = list()
		# need_start.append("analize")
		# need_start.append('updater')
		# need_start.append('buyer')
		need_start.append("seller")
		need_start.append('balanceCalc')

		Main(need_start)

	if USE_BOT:
		MainWithBot()