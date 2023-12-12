import ccxt
from connectors.bitteam import BitTeam
from connectors.data_base import RequestsDataBase
from connectors.exchange import Exchange

ACCOUNT_1 =  'Luchnik_Mexc' # 'Constantin_BitTeam'
ACCOUNT_2 =  'Luchnik_BitTeam'
ACCOUNT_3 =  'Luchnik_ByBit'
div_line = '-------------------------------------------------------------------------------------'

accounts = [ACCOUNT_1, ACCOUNT_2, ACCOUNT_3]
dbs = [RequestsDataBase(account_name=account, bot_name='', order_table='') for account in accounts]
connects = [Exchange(db) for db in dbs]
exchanges = [connect.exchange for connect in connects]
balances = [connect.get_balance() for connect in connects]
# instanses_mexc = [isinstance(exchange, ccxt.mexc) for exchange in exchanges]
# instanses_bitteam = [isinstance(exchange, BitTeam) for exchange in exchanges]
# instanses_bybit = [isinstance(exchange, ccxt.bybit) for exchange in exchanges]

print(f"Аккаунты:", *accounts, div_line, sep='\n')
print(f"Подключения к Базе Данных:", *dbs, div_line, sep='\n')
print(f"Соединения:",*connects, div_line, sep='\n')
[print(f"Баланс Биржи: {exchanges[i]}", balances[i], div_line, sep='\n') for i in range(len(exchanges))]
# print('Биржа принадлежит классу MEXC:', instanses_mexc, div_line, sep='\n')
# print('Биржа принадлежит классу BitTeam:', instanses_bitteam, div_line, sep='\n')
# print('Биржа принадлежит классу ByBit:', instanses_bybit, div_line, sep='\n')
