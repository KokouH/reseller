
import datetime
from sqlalchemy import Column, String, INTEGER, FLOAT, BOOLEAN, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class ItemsBase(Base):
	__tablename__ = "ItemsBase"
	hash_name = Column(String, primary_key=True)
	appid = Column(String)
	steamid = Column(String)
	buy_price = Column(INTEGER)
	sell_price = Column(INTEGER)
	count_buy = Column(INTEGER)
	trend_7d = Column(FLOAT)
	trend_30d = Column(FLOAT)
	sells_7d = Column(INTEGER)
	sells_30d = Column(INTEGER)
	sell_price_conf = Column(FLOAT)
	buy_price_deep = Column(FLOAT)
	history_stable = Column(BOOLEAN)
	time_updated = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, primary_key=True)

	def __repr__(self):
		return f"\
			{self.hash_name} \
			{self.buy_price} \
			{self.sell_price} \
			{self.count_buy} \
			{self.trend_30d} \
			{self.sells_30d}\n"
	
	def __str__(self):
		return f"{self.hash_name} \
{self.appid} \
{self.steamid} \
{self.buy_price} \
{self.sell_price} \
{self.count_buy} \
{self.trend_7d} \
{self.trend_30d} \
{self.sells_7d} \
{self.sells_30d} \
{self.sell_price_conf} \
{self.buy_price_deep} \
{self.history_stable} \
{self.time_updated}"

if __name__ == "__main__":
	engine = create_engine("sqlite:///database/market.db")
	Base.metadata.create_all(bind=engine)
	Session = sessionmaker()
	Session.configure(bind=engine)
	session = Session()

	# print(session.query(ItemsBase).first())
	f_items = session.query(ItemsBase).filter(
			ItemsBase.trend_30d >= .99,
			ItemsBase.trend_30d <= 1.3,
			ItemsBase.trend_7d >= .99,
			ItemsBase.sells_30d >= 70,
			ItemsBase.history_stable == True,
			ItemsBase.buy_price_deep <= 5,
			ItemsBase.buy_price >= .1,
			# ItemsBase.sell_price_conf >= .08
		).all()

	all_table = session.query(ItemsBase).all()
	at_by_time = sorted(all_table, key=lambda m: m.time_updated)
	print(f"Len table {len(all_table)}")
	print(f"Filtered items len: {len(f_items)}")
	print(f"Max turnover amount: {sum(i.buy_price * i.count_buy / 2 for i in f_items)}$")
	print(f"Collect time {at_by_time[-1].time_updated - at_by_time[0].time_updated}")
	
	import matplotlib.pyplot as plt
	print(at_by_time[0])
	print(at_by_time[-1].time_updated, at_by_time[-1].hash_name)
	y = [(i.time_updated - at_by_time[0].time_updated).total_seconds() for i in at_by_time]
	x = [i for i in range(len(at_by_time))]
	plt.subplot(1,2, 1)
	plt.plot(x, y)

	x = x[:-1]
	y1 = []
	for i in range(1, len(y)):
		y1.append( y[i] - y[i - 1] )
	plt.subplot(1,2,2)
	plt.plot(x, y1)
	# plt.show()