import pandas as pd
import ccxt
import sqlite3 as sq
from time import sleep, time, localtime, strftime
import random
import json
# import multiprocessing as mp

from connectors.bitteam import BitTeam
# from config_2slabs_bitteam import *
# from config_neighbour_bitteam import *
from data_bases.path_to_base import DATABASE
ACCOUNT = 'Constantin_BitTeam'

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



def main():

    exchange = connect_exchange()
    balance = get_balance(exchange)
    # print(balance)

    # order_book = exchange.fetch_order_book(SYMBOL)
    # print(order_book)
    my_trades = exchange.fetch_my_trades(SYMBOL)
    print(my_trades)



main()
