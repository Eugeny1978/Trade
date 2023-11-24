import pandas as pd
import ccxt
import sqlite3 as sq
from time import sleep, time, localtime, strftime
import random
import json
# import ccxt
# import multiprocessing as mp

from connectors.bitteam import BitTeam
from config_2slabs_bitteam import *
from data_bases.path_to_base import DATABASE

pd.options.display.width= None # Отображение Таблицы на весь Экран
pd.options.display.max_columns= 20 # Макс Кол-во Отображаемых Колонок

def get_apikeys(account_name):
    with sq.connect(DATABASE) as connect:
        connect.row_factory = sq.Row  # Строки записей в виде dict {}. По умолчанию - кортежи turple ()
        curs = connect.cursor()
        curs.execute("""SELECT apiKey, secret FROM Apikeys WHERE account LIKE ? AND name LIKE 'Info' LIMIT 1""", (account_name,))
        keys = curs.fetchone()
        return {'apiKey': keys['apikey'], 'secret': keys['secret']}

def connect_exchange():
    apikeys = get_apikeys(ACCOUNT)
    try:
        exchange = BitTeam(apikeys)
        return exchange
    except Exception as error: # проверка на подключение
        raise print(error)

def get_balance(exchange):
    balance = exchange.fetch_balance()
    indexes = ['free', 'used', 'total']
    columns = [balance['free'], balance['used'], balance['total']]
    df = pd.DataFrame(columns, index=indexes)
    df_0 = df.loc[:, (df != 0).any(axis=0)]  # убирает Столбцы с 0 значениями
    df_compact = df_0.loc[:, (df_0 != '0').any(axis=0)]  # если числа в виде строк
    return df_compact

def get_trade_ids(exchange):
    trades = exchange.fetch_my_trades(SYMBOL)['result'] # "makerOrderId": 107007160
    trade_ids = []
    if trades['count'] > 0:
        for trade in trades['trades']:
            trade_ids.append(str(trade['makerOrderId']))
    return trade_ids


def main():

    exchange = connect_exchange()
    # balance = get_balance(exchange)
    # print(balance)
    # orders = exchange.fetch_orders(SYMBOL)
    # print(json.dumps(orders))
    # order_book = exchange.fetch_order_book(SYMBOL)
    # print(order_book)

    # # Нельзя списком
    # # {"message": "\"id\" must be a string", "path": ["id"], "type": "string.base", "context": {"label": "id", "value": ["106924207", "106924184"], "key": "id"}}
    # cancel = exchange.cancel_order(id=['106924207', '106924184'])
    # print(json.dumps(cancel))
    # orders = exchange.fetch_orders(SYMBOL)['result']['orders']
    # print(orders)
    # start = time()
    # for order in orders:
    #     exchange.cancel_order(id=order['id'])
    # print(f'Прошло времени {time() - start} сек.')

    # sell_order = exchange.create_order(SYMBOL,type='limit', side='sell', amount=200, price=0.0185)
    # print(sell_order)M
    #     # buy_order = exchange.create_order(SYBOL, type='limit', side='buy', amount=200, price=0.0165)
    # print(buy_order)

    # print(get_trade_ids(exchange))
    t = localtime()
    current_time = strftime("%H:%M:%S", t)
    print(current_time)






    # ccxt.binance.fetch_my_trades()



main()
