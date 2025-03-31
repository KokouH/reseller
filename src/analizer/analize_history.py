
from config import *
from typing import List, Tuple
from accounts import accounts

def collect_all_history(acc: accounts.Account) -> Tuple[List, List]:
	resp = acc._steam_client._session.get(f"https://steamcommunity.com/market/myhistory?norender=1&count=500").json()
	tc = resp['total_count']

	bev = [ev for ev in resp['events'] if ev['event_type'] == 4]
	sev = [ev for ev in resp['events'] if ev['event_type'] == 3]
	
	q = lambda e: resp['purchases'][f"{e['listingid']}_{e['purchaseid']}"] # get purchase
	qr = lambda e: q(e)['asset']['id']
	qw = lambda e: resp['assets']['440']['2'][qr(e)] if qr(e) in resp['assets']['440']['2'] else resp['assets']['252490']['2'].get(qr(e)) # get asset

	buys = [[qw(e)['market_hash_name'], q(e)['paid_amount'] + q(e)['paid_fee']] * int(q(e)['asset']['amount']) for e in bev]
	sells = [[qw(e).get('market_hash_name'), q(e)['received_amount']] for e in sev if qw(e)]

	return (sells, buys)

def cals_delta(sells: List, buys: List):
	buyed = 0
	sold = 0
	l = list()
	buys = list(buys)
	for sell in sells:
		name = sell[0]
		ind = next((i for i, item in enumerate(buys) if item[0] == name), None)
		if ind:
			sold += sell[1]
			buyed += buys[ind][1]
			l.append(sell[1] - buys[ind][1])
			del(buys[ind])
		else:
			break;
	return (buyed, sold, l)


accs = accounts.Accounts()
# accs.add(accounts.Account( *acc_data_1 ))
# accs.add(accounts.Account( *acc_data_2 ))
# accs.add(accounts.Account( *acc_data_3 ))
accs.add(accounts.Account( *acc_data_4 ))

# print(cals_delta( *(collect_all_history(accs.get_accounts()[0])) ))

