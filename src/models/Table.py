from sqlalchemy import Column, String, INTEGER, FLOAT, BOOLEAN
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class Items(Base):
	__tablename__ = "Items"
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

	def __repr__(self):
		return f"\
			{self.hash_name} \
			{self.buy_price} \
			{self.sell_price} \
			{self.count_buy} \
			{self.trend_30d} \
			{self.sells_30d}\n"
	
	def __str__(self):
		return f"\
			{self.hash_name} \
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
			{self.history_stable}"

if __name__ == "__main__":
	engine = create_engine("sqlite:///database/market.db", echo=True)
	Base.metadata.create_all(engine)
	Session = sessionmaker()
	Session.configure(bind=engine)
	session = Session()
	# item = Items(hash_name='asdf',
	# 		  appid='123',
	# 		  steamid='123',
	# 		  buy_price=123,
	# 		  sell_price=32,
	# 		  count_buy=20,
	# 		  trend_7d=1.1,
	# 		  trend_30d=1.2)
	# session.add(item)
	print(session.query(Items).all())