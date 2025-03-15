
from config import *
from accounts import accounts
from time import sleep
from random import random
from models.Table import ItemsBase
from utils.TelegramBot import send_message

from loguru import logger
from steampy.models import GameOptions
from steampy.exceptions import ApiException
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import asyncio

import matplotlib.pyplot as plt
import numpy as np

"""
TODO
Добавить диаграммы:
1 Круговые
1.1 Общая распределение баланса инвентаря и ордеров +
1.2 Балансов( вл бал, инв, орд ) распределение по аккаунтам +

2 Графики изменения
2.1 Добавить логирование
2.2 Показать динамику ценностей
2.3 График скорости дохода( производная по 2.2 )
"""

def main(accs: accounts.Accounts):

	engine = create_engine("sqlite:///database/market.db")
	Session = sessionmaker()
	Session.configure(bind=engine)
	session = Session()

	# balance + sell orders + inventory

	all_balances = 0.0
	all_sellOrders = 0.0
	all_invs = 0.0

	l_all_balances = list()
	l_all_sellOrders = list()
	l_all_invs = list()

	not_calc_items = {} # hash_name: count
	for acc in accs.get_accounts():
		logger.info(f"Start collect info of {acc.username[:5]}")
		# BALANCE
		try:
			bal = float(acc._steam_client.get_wallet_balance(with_hold=True))
			all_balances += bal
			l_all_balances.append(bal)
			logger.info("Balance recived")
		except ApiException as e:
			logger.error(f"Can't get sell_orders for: {acc.username[:5]}")
		sleep(random() * 2 + 2)

		# SELL ORDERS
		try:
			sell_orders = list(acc._steam_client.market.get_my_market_listings()['sell_listings'].values())
			val = sum(float(order["you_receive"].replace('$', '').replace(' USD', '').replace(' each', '')) * int(order['description']['amount']) for order in sell_orders)
			all_sellOrders += val
			l_all_sellOrders.append(val)
			logger.info("Orders recived")
		except ApiException as e:
			logger.error(f"Can't get sell_orders for: {acc.username[:5]}")
		sleep(random() * 2 + 2)

		# INVENTORY
		inv_val = 0.0
		try:
			inv = list(acc._steam_client.get_my_inventory(GameOptions.RUST).values())
			for item in inv:
				hash_name = item['market_hash_name']
				t_item = session.query(ItemsBase).filter(ItemsBase.hash_name == hash_name, ItemsBase.appid == GameOptions.RUST.app_id).first()
				if t_item:
					val = t_item.sell_price * .87 * int(item['amount'])
					all_invs += val
					inv_val += val
				else:
					if hash_name not in not_calc_items:
						not_calc_items[hash_name] = 0
					not_calc_items[hash_name] += int(item['amount'])
		except ApiException as e:
			logger.error(f"Can't get RUST inv for: {acc.username[:5]}")
		sleep(random() * 2 + 2)

		inv = []
		for _ in range(3):
			try:
				inv = list(acc._steam_client.get_my_inventory(GameOptions.TF2).values())
				break;
			except ApiException as e:
				logger.error(f"Can't get TF2 inv for: {acc.username[:5]}")
		for item in inv:
			hash_name = item['market_hash_name']
			t_item = session.query(ItemsBase).filter(ItemsBase.hash_name == hash_name, ItemsBase.appid == GameOptions.TF2.app_id).first()
			if t_item:
				val = t_item.sell_price * .87 * int(item['amount'])
				all_invs += val
				inv_val += val
			else:
				if hash_name not in not_calc_items:
					not_calc_items[hash_name] = 0
				not_calc_items[hash_name] += int(item['amount'])
		logger.info("Inventory recived")
		l_all_invs.append(inv_val)
		sleep(random() * 2 + 2)

	for name in not_calc_items:
		recv = float(input(f"Price for {name}: ")) * not_calc_items[name]
		all_invs += recv

	all_balances = int(all_balances)
	all_sellOrders = int(all_sellOrders)
	all_invs = int(all_invs)
	mes = f"All balances: {all_balances}\nAll sell_orders: {all_sellOrders}\nAll inv items: {all_invs}\nAll networs: {all_balances + all_sellOrders + all_invs}"
	asyncio.run(send_message(mes))

	for i, acc in enumerate(accs.get_accounts()):
		mes = f"{acc.username[:5]}\nBalance: {l_all_balances[i]:.2f}\nInventory: {l_all_invs[i]:.2f}\nSell orders: {l_all_sellOrders[i]:.2f}"
		asyncio.run(send_message(mes))

	session.close

	if __name__ == "__main__":
		plt.figure()
		ax = plt.subplot(2, 1, 1)
		data = [all_balances, all_sellOrders, all_invs]
		labels = ["Балансы %.2f" % all_balances, "Ордера  %.2f" % all_sellOrders, "Инвентари %.2f" % all_invs]
		ax.pie(data, labels=labels, autopct='%.2f')

		ax = plt.subplot(2, 1, 2)
		data = [str(sum([l_all_balances[i], l_all_sellOrders[i], l_all_invs[i]])) for i in range(len(l_all_balances))]
		labels = [acc.username[:5] for acc in accs.get_accounts()]
		ax.pie(data, labels=labels, autopct="%.2f")

		plt.figure()
		for i, acc in enumerate( accs.get_accounts() ):
			ax = plt.subplot(2, 2, i + 1)
			data = [l_all_balances[i], l_all_sellOrders[i], l_all_invs[i]]
			labels = ['Баланс %.2f' % l_all_balances[i], 'Ордера %.2f' % l_all_sellOrders[i], 'Инвентарь %.2f' % l_all_invs[i],]
			ax.set_title(acc.username[:5])
			ax.pie(data, labels=labels, autopct='%.2f')

		plt.show()

if __name__ == "__main__":
	accs = accounts.Accounts()
	accs.add(accounts.Account( *acc_data_1 ))
	sleep(random() * 2 + 1)
	accs.add(accounts.Account( *acc_data_2 ))
	sleep(random() * 2 + 1)
	accs.add(accounts.Account( *acc_data_3 ))
	sleep(random() * 2 + 1)
	accs.add(accounts.Account( *acc_data_4 ))

	main(accs)
