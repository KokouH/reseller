
from config import *
from accounts import accounts
from time import sleep
from random import random
from models.Table import ItemsBase

from loguru import logger
from steampy.models import GameOptions
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import matplotlib.pyplot as plt
import numpy as np

"""
TODO
Добавить диаграммы:
1 Круговые
1.1 Общая распределение баланса инвнтаря и оредров +
1.2 Балансов( вл бал, инв, орд ) распрделение по аккаунтам +

2 Графики изменения
2.1 Добавить логирование
2.2 Показать динамику ценностей
2.3 График скорости дохода( производная по 2.2 )
"""

# if __name__ == "__main__":
	
accs = accounts.Accounts()
accs.add(accounts.Account( *acc_data_1 ))
sleep(random() * 2 + 1)
accs.add(accounts.Account( *acc_data_2 ))
sleep(random() * 2 + 1)
accs.add(accounts.Account( *acc_data_3 ))
sleep(random() * 2 + 1)
accs.add(accounts.Account( *acc_data_4 ))

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
	logger.info(f"Start collect info of {acc.username}")
	# BALANCE
	all_balances += float(acc._steam_client.get_wallet_balance())
	l_all_balances.append(float(acc._steam_client.get_wallet_balance()))
	sleep(random() * 2 + 2)
	logger.info("Balance recived")

	# SELL ORDERS
	sell_orders = list(acc._steam_client.market.get_my_market_listings()['sell_listings'].values())
	val = sum(float(order["you_receive"].replace('$', '').replace(' USD', '').replace(' each', '')) * int(order['description']['amount']) for order in sell_orders)
	all_sellOrders += val
	l_all_sellOrders.append(val)
	sleep(random() * 2 + 2)
	logger.info("Orders recived")

	# INVENTORY
	inv_val = 0.0
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
	sleep(random() * 2 + 2)
	inv = list(acc._steam_client.get_my_inventory(GameOptions.TF2).values())
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
	sleep(random() * 2 + 2)
	l_all_invs.append(inv_val)
	logger.info("Inventory recived")

for name in not_calc_items:
	recv = float(input(f"Price for {name}: ")) * not_calc_items[name]
	all_invs += recv

print(f"All balances: {all_balances}\nAll sell_orders: {all_sellOrders}\nAll inv items: {all_invs}")
print(f"All networs: {all_balances + all_sellOrders + all_invs}")

plt.figure()
ax = plt.subplot(2, 1, 1)
data = [all_balances, all_sellOrders, all_invs]
labels = ["Балансы %.2f" % all_balances, "Ордера  %.2f" % all_sellOrders, "Инвентари %.2f" % all_invs]
ax.pie(data, labels=labels, autopct='%.2f')

ax = plt.subplot(2, 1, 2)
data = [str(sum([l_all_balances[i], l_all_sellOrders[i], l_all_invs[i]])) for i in range(len(l_all_balances))]
labels = [acc.username for acc in accs.get_accounts()]
ax.pie(data, labels=labels, autopct="%.2f")

plt.figure()
for i, acc in enumerate( accs.get_accounts() ):
	ax = plt.subplot(2, 2, i + 1)
	data = [l_all_balances[i], l_all_sellOrders[i], l_all_invs[i]]
	labels = ['Баланс %.2f' % l_all_balances[i], 'Ордера %.2f' % l_all_sellOrders[i], 'Инвентарь %.2f' % l_all_invs[i],]
	ax.set_title(acc.username)
	ax.pie(data, labels=labels, autopct='%.2f')

plt.show()
