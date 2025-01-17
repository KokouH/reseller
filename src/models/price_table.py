
import redis
from config import *
from typing import List

class TableLine:
    def __init__(self):
        self.hash_name: str = ''
        self.buy_price: int = -1
        self.sell_price: int = -1
        self.month_sells: int = -1
        self.trend: float = 0.0
        self.updatetime: int = 0

    def __str__(self):
        return f"{self.hash_name}:{self.buy_price}:{self.sell_price}:{self.month_sells}:{self.trend}:{self.updatetime}"

class PriceTable:
    CS: List[TableLine] = list()
    RUST: List[TableLine] = list()
    DOTA2: List[TableLine] = list()

    def addLine(
            game:str,
            tableLine: TableLine):
        if game not in ('cs2', 'dota', 'rust'):
            raise ValueError("Wrong game name")
        print(str(tableLine))
        PriceTable._r.zadd(
            game,
            {str(tableLine):f"{game}:{tableLine.hash_name}"},
            nx=True
        )

    def updateLine(
            game:str,
            tableLine: TableLine):
        if game not in ('cs2', 'dota', 'rust'):
            raise ValueError("Wrong game name")
        PriceTable._r.zadd(
            game,
            {str(tableLine):f"{game}:{tableLine.hash_name}"},
            xx=True,
            ch=True
        )

    __pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
    _r = redis.Redis(connection_pool=__pool)
    _r.ping()

if __name__ == "__main__":
    PriceTable.addLine('rust', TableLine())