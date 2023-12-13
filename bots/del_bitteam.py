from time import sleep
from connectors.bitteam import BitTeam
import json
import sqlite3 as sq
import pandas as pd
from random import uniform

from data_bases.path_to_base import DATABASE

SYMBOL = 'DEL/USDT'
pd.options.display.width= None # Отображение Таблицы на весь Экран
pd.options.display.max_columns= 20 # Макс Кол-во Отображаемых Колонок
div_line = '-------------------------------------------------------------------------------------'
VOLUME = 80000 # 150000
NUM_SLISES = 150 # 50
START_PRICE = 0.021 # 0.023
PRICE_STEP = 0.000010 # ?
AMOUNT_ACCURACY = 6

def get_api_keys(name_account):
    with sq.connect(DATABASE) as connect:
        connect.row_factory = sq.Row  # строки записей в виде dict {}. По умолчанию - кортежи turple ()
        curs = connect.cursor()
        curs.execute("""SELECT * FROM Apikeys WHERE account LIKE ?""", [name_account])
        account = curs.fetchone()
        keys = {'apiKey': account['apikey'], 'secret': account['secret']}
        return keys

def print_json(data):
    print(json.dumps(data))

def connect_exchange():
    api_keys = get_api_keys('Constantin_BitTeam')  # 'Luchnik_BitTeam'
    exchange = BitTeam(api_keys)
    return exchange

def get_slises():
    nominal_slice = VOLUME / NUM_SLISES
    slices = []
    for i in range(1, NUM_SLISES):
        slices.append(round(uniform(0.8 * nominal_slice, 1.2 * nominal_slice), AMOUNT_ACCURACY))
    slice_subsum = sum(slices)
    if VOLUME > slice_subsum:
        slices.append(round(VOLUME - slice_subsum, AMOUNT_ACCURACY))
    print(slices)
    return slices

def create_my_orders(exchange, slices):
    price = START_PRICE
    orders = []
    for slice in slices:
        sell_order = exchange.create_order(SYMBOL, type='limit', side='sell', amount=slice, price=price)['result']
        orders.append(sell_order)
        price += PRICE_STEP
        sleep(1)
    return orders

def main_slices():
    exchange = connect_exchange()
    exchange.cancel_all_orders(SYMBOL)
    slices = get_slises()

    orders = create_my_orders(exchange, slices)
    print_json(orders)
    print(div_line)

    orders_exchange = exchange.fetch_orders(SYMBOL)
    print_json(orders_exchange)

def main_buy():
    exchange = connect_exchange()
    price = 0.016003
    # exchange.create_order(SYMBOL, type='limit', side='buy', amount=round(28650/price, 6), price=price)
    exchange.create_order(SYMBOL, type='limit', side='buy', amount=740735, price=0.015000)
    exchange.create_order(SYMBOL, type='limit', side='buy', amount=475855, price=0.014900)
    exchange.create_order(SYMBOL, type='limit', side='buy', amount=740735, price=0.014800)


def main_cancel():
    exchange = connect_exchange()
    exchange.cancel_all_orders(SYMBOL)

def main_watch_orders():
    exchange = connect_exchange()
    orders = exchange.fetch_orders(SYMBOL)
    print_json(orders)

# main_slices()
# main_buy()
# main_cancel()
# main_watch_orders()
