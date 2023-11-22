import ccxt
import json
import pandas as pd
import sqlite3 as sq
from time import sleep
import multiprocessing as mp
import random
from typing import Literal, get_args  # Создание Классов Перечислений

LevelType = Literal['slab_1', 'slab_2', 'carrots', None]

from config_2slabs_mexc import *
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

def get_trade_mode(account_name):
    with sq.connect(DATABASE) as connect:
        connect.row_factory = sq.Row  # Строки записей в виде dict {}. По умолчанию - кортежи turple ()
        curs = connect.cursor()
        curs.execute("""SELECT type FROM Accounts WHERE name LIKE ?""",(account_name,))
        mode = curs.fetchone()[0]
        return mode

def connect_exchange():
    apikeys = get_apikeys(ACCOUNT)
    trade_mode = get_trade_mode(ACCOUNT)
    try:
        exchange = ccxt.mexc(apikeys)
        if trade_mode == 'test': exchange.set_sandbox_mode(True)
        exchange.load_markets()
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

def print_json(dict_value):
    print('-------------------------------------------------------------------------')
    print(json.dumps(dict_value))
    print('-------------------------------------------------------------------------')

def get_id_orders_sql(name):
    with sq.connect(DATABASE) as connect:
        curs = connect.cursor()
        curs.execute("""SELECT id FROM orders_2slabs WHERE name LIKE ?""", (name,))
        ids = []
        for select in curs:
            ids.append(select[0])
        return ids

def cancel_orders_exchange(exchange, name):
    id_orders = get_id_orders_sql(name)
    for id in id_orders:
        try:
            exchange.cancel_order(id=id, symbol=SYMBOL)
            print(f'Удален Ордер ID: {id}')
        except Exception as error:
            print(f'Нет Ордера с id: {id} | {error}')

def synchronize_orders(exchange, name):
    # Ордера (ID) с необходимым именем в БД
    sql_id_orders = get_id_orders_sql(name)
    if not len(sql_id_orders):
        print(f'В БД НЕТ ордеров с именем: {name}')
        return None

    # Все Открытые Ордера (ID)
    opened_orders = exchange.fetch_open_orders(SYMBOL)

    opened_id_orders = []
    if not len(opened_orders):
        print(f'НЕТ ОТКРЫТЫХ ордеров')
    else:
        for order in opened_orders:
            opened_id_orders.append(int(order['id']))
    print(f'Список ордеров в БД: {sql_id_orders}')
    print(f'Список ОТКРЫТЫХ ордеров: {opened_id_orders}')

    # Формимрование Списка Ордеров на Удаление из БД (в Базе есть а на Бирже Отсутствуют (Исполнены или что-то другое))
    id_for_delete = []
    for id in sql_id_orders:
        if id not in opened_id_orders:
            id_for_delete.append(id)

    # Удаление Ордеров из БД
    if len(id_for_delete):
        with sq.connect(DATABASE) as connect:
            curs = connect.cursor()
            ids = ','.join(map(str, id_for_delete))
            curs.execute(f"DELETE FROM orders_2slabs WHERE id IN ({ids})")

    return True

def cancel_orders(exchange, name):
    sync = synchronize_orders(exchange, name)
    if not sync:
        return None
    cancel_orders_exchange(exchange, name)
    synchronize_orders(exchange, name)


def main():
    print(LevelType)
    print(get_args(LevelType)[1])

    # # Инициализация.
    # exchange = connect_exchange()
    # balance = get_balance(exchange)
    # print(balance)
    # print('-------------------------------------')

    # order = exchange.create_order(SYMBOL, 'limit', 'sell', 5, 3.0000)
    # opened_orders = exchange.fetch_open_orders(SYMBOL)
    # print_json(opened_orders)

    # exchange.cancel_all_orders(SYMBOL)
    # cancel_orders(exchange, 'carrots')


    #

    # closed_orders = exchange.fetch_closed_orders(SYMBOL)
    # canceled_orders = exchange.fetch_canceled_orders(SYMBOL)

    # all_orders = exchange.fetch_orders(SYMBOL)
    # # order_id = exchange.fetch_order(symbol=SYMBOL, id='')

    # my_trades = exchange.fetch_my_trades(SYMBOL) # мои сделки трейды

    # order = exchange.create_order(SYMBOL, 'limit', 'sell', 0.07, 2200)
    # opened_orders = exchange.fetch_open_orders(SYMBOL)
    # print_json(opened_orders)


    # print_json(closed_orders)
    # print_json(canceled_orders)
    #
    # print_json(all_orders)
    # print_json(my_trades)
    # print_json(order)



# ---- RUN -----------------------------------------------------------------------------------
main()