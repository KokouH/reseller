import datetime
import pandas as pd
import numpy as np
from typing import List

# Main params
min_sells_per_month = 60

# Spike clean params
WINDOW_SIZE = 10
THRESHOLD_MULTIPLIER = 2.5

# Stable check
THRESHOLD_STABLE = 0.4

# def remove_spikes(history: List) -> List:
# 	df = pd.DataFrame([i[1] for i in history], columns=['Value'])
# 	window_size = WINDOW_SIZE
# 	threshold_multiplier = THRESHOLD_MULTIPLIER 

# 	df['Rolling_Mean'] = df['Value'].rolling(window=window_size).mean()
# 	df['Rolling_Std'] = df['Value'].rolling(window=window_size).std()
# 	df['Spike'] = (df['Value'] > (df['Rolling_Mean'] + threshold_multiplier * df['Rolling_Std'])) | \
# 				(df['Value'] < (df['Rolling_Mean'] - threshold_multiplier * df['Rolling_Std']))
# 	clean_history = list()
# 	for i, val in enumerate(df['Spike']):
# 		if not val:
# 			clean_history.append(history[i])

# 	return clean_history

def remove_spikes(history: List):
    df = pd.DataFrame([i[1] for i in history], columns=['Value'])
    q1 = df['Value'].quantile(0.25)
    q3 = df['Value'].quantile(0.75)
    iqr = q3 - q1
    df['Spike'] = (df['Value'] > q3 + 1.5 * iqr) | (df['Value'] < q1 - 1.5 * iqr)

    return list([history[i] for i in df[~df['Spike']].index])

def get_last_n_days(history: List, n: int) -> List:
	last_history = []
	now_datetime = datetime.datetime.now()
	delta = datetime.timedelta(days=n)
	for i in reversed(history):
		if now_datetime - i[0] > delta:
			break;
		last_history.append(i)

	return list(reversed(last_history))

def get_last_month(history: List) -> List:
	return get_last_n_days(history, 30)

def get_sells_n_days(history: List, n: int) -> int:
	history = get_last_n_days(history, n)
	history = remove_spikes(history)
	sells = 0

	for i in history:
		sells += int(i[2])
	
	return sells

def get_month_sells(history: List) -> int:
	return get_sells_n_days(history, 30)

def get_week_sells(history: List) -> int:
	return get_sells_n_days(history, 7)

def get_deep_in_cup(histogram, month_sells, buy_price: float) -> float:
	count = 0
	for i in histogram['buy_order_graph']:
		if buy_price < i[0]:
			break;
		if buy_price == i[0]:
			count = i[1]
			break;
		count = i[1]
	return count * 30 / month_sells

def get_trend_n_days(history: List, n: int):
	history = get_last_n_days(history, n)
	history = remove_spikes(history)
		
	y = np.array([i[1] for i in  history])
	x = np.array([i for i in range(len(history))])
	z = np.polyfit(x, y, 1)
	p = np.poly1d(z)

	return p(x[-1]) / p(x[0])

def get_trend_month(history: List):
	return get_trend_n_days(history, 30)

def get_trend_week(history: List):
	return get_trend_n_days(history, 7)

def get_sell_in_history(history: List, sell_price: float) -> float:
	history = get_last_month(history)
	history = remove_spikes(history)

	all_sells = 0
	for i in history:
		all_sells += int(i[2])

	above_sells = 0
	for i in history:
		if i[1] >= sell_price:
			above_sells += int(i[2])

	return above_sells / all_sells

# def get_history_stable(history: List) -> bool:
# 	history = get_last_month(history)
# 	history = remove_spikes(history)

# 	data = pd.Series([i[1] for i in history])
# 	ws = int(min_sells_per_month / 15) # window size 2 days
# 	moving_average = data.rolling(window=ws).mean()
# 	std_dev = np.std(moving_average.dropna())

# 	return (std_dev < THRESHOLD_STABLE)

def get_volatility(history: List):
	history = get_last_month(history)
	history = remove_spikes(history)

	prices = [i[1] for i in history]
	volatility = np.std(prices) / np.mean(prices)
	return volatility

def get_reference_price(history: List) -> float:
	history = get_last_n_days(history, 4)
	history = remove_spikes(history)
	
	if not len(history):
		return 0.0
	
	reference_price = max(float(i[1]) for i in history)
	return reference_price