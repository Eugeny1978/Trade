from connectors.data_base import RequestsDataBase

ACCOUNT =  'Luchnik_Mexc' # 'Constantin_BitTeam'
ACCOUNT_BitTeam =  'Luchnik_BitTeam' # 'Constantin_BitTeam'
ORDER_TABLE = 'orders_2slabs_mexc'
BOT_NAME = 'bot_2slabs_mexc'
div_line = '-------------------------------------------------------------------------------------'
orders = [
    {'id': 10000, 'symbol': 'DEL/USDT', 'type': 'limit', 'side': 'buy', 'amount': 5000, 'price': 0.015000},
    {'id': 11000, 'symbol': 'DEL/USDT', 'type': 'limit', 'side': 'buy', 'amount': 4000, 'price': 0.015500},
    {'id': 12000, 'symbol': 'DEL/USDT', 'type': 'limit', 'side': 'buy', 'amount': 6000, 'price': 0.014500},
]

db = RequestsDataBase(ACCOUNT, BOT_NAME, ORDER_TABLE)
[db.write_order(order, name='carrots') for order in orders]
ids = db.get_id_orders()
db.delete_old_orders(old_ids=ids)

print(div_line)
print(f"Атрибуты Класса: {db} | __dict__ ", db.__dict__, div_line, sep='\n')
print(f"get_id_orders(): {ids}", div_line, sep='\n')
print(f"get_bot_status(): {db.get_bot_status()}", div_line, sep='\n')

