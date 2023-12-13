from connectors.bitteam import BitTeam
from connectors.data_base import RequestsDataBase
from time import sleep
ACCOUNT = 'Constantin_BitTeam' # 'Luchnik_BitTeam'
SYMBOL_1 = 'DEL/USDT'
SYMBOL_2 = 'ETH/USDT'
div_line = '-------------------------------------------------------------------------------------'

exchange = BitTeam()

# order_book = exchange.fetch_order_book()
# print(order_book)
# best_ask = order_book['result']['asks'][0]
# print(best_ask)

# tiker = exchange.fetch_ticker()
# tiker1 = exchange.fetch_ticker(SYMBOL_1)
# tiker2 = exchange.fetch_ticker(SYMBOL_2)
# print(tiker, tiker1, tiker2, sep='\n\n')

# symbols = exchange.info_symbols()
# print(symbols)

data_base = RequestsDataBase(ACCOUNT)
exchange.account = data_base.apikeys

# balance = exchange.fetch_balance()
# print(balance)
# print(div_line)
# print(exchange.data)

# # create_order(self, symbol: str, type: OrderType, side: OrderSide, amount: float, price: float)
# order = exchange.create_order(symbol=SYMBOL_1, type='limit', side='sell', amount=550, price=0.020)
# print(order)
# # # print(exchange.cancel_order(109736279))
# canceled_order = exchange.cancel_order(order['result']['id'])
# print(canceled_order)

# prices = [0.02, 0.021, 0.022]
# orders = [exchange.create_order(SYMBOL_1, type='limit', side='sell', amount=300, price=price) for price in prices]
# print(*orders, sep='\n')
# # canceled_orders = exchange.cancel_all_orders(SYMBOL_1)
# canceled_orders = exchange.cancel_all_orders()
# print(canceled_orders)
# print('\n\n')
# sleep(1)
# print(exchange.fetch_balance())

# order = exchange.create_order(symbol=SYMBOL_1, type='limit', side='sell', amount=500, price=0.020)
# fetch = exchange.fetch_order(order['result']['id'])
# print(fetch)
# exchange.cancel_all_orders()

# limit_order = exchange.create_order(SYMBOL_1, type='limit', side='sell', amount=1000, price=0.02)
# print(limit_order, div_line, sep='\n')
# market_order = exchange.create_order(SYMBOL_1, type='market', side='sell', amount=1000)
# print(market_order, div_line, sep='\n')
# orders = exchange.fetch_orders()
# print(orders)


# prices = [0.021, 0.022, 0.023]
# [exchange.create_order(SYMBOL_1, type='limit', side='sell', amount=300, price=price) for price in prices]
# sleep(1)
# orders = exchange.fetch_orders()
# print(orders)
# exchange.cancel_all_orders()

# trades = exchange.fetch_my_trades()
# trades = exchange.fetch_my_trades(SYMBOL_1)
# print(trades)






