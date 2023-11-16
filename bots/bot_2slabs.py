import asyncio
import ccxt
import json
import pandas as pd
import sqlite3 as sq
from config_2slabs import *
from time import sleep
import multiprocessing as mp
import random

from data_bases.path_to_base import DATABASE

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
        exchange = ccxt.binance(apikeys)
        if trade_mode == 'test': exchange.set_sandbox_mode(True)
        exchange.load_markets()
        return exchange
    except Exception as error: # проверка на подключение
        raise print(error)

def get_decimal(arg: list):
    decimals = []
    for value in arg:
        value_str = str(value)
        if '.' in value_str:
            decimals.append(len(value_str.split('.')[1]))
        else:
            decimals.append(0)
    max_decimal = max(decimals)
    return max_decimal

def get_params_symbol(exchange):
    data = exchange.fetch_ticker(SYMBOL)

    step_price = get_decimal([data['open'], data['close'], data['high'], data['low']])
    step_volume = get_decimal([data['bidVolume'], data['askVolume'], data['baseVolume']])
    start_price = round(((data['ask'] + data['bid']) / 2), step_price)
    # params = {'start_price': start_price, 'decimal_price': step_price, 'decimal_volume': step_volume}
    # return params
    return (start_price, step_price, step_volume)

def get_balance(exchange):
    balance = exchange.fetch_balance()
    indexes = ['free', 'used', 'total']
    columns = [balance['free'], balance['used'], balance['total']]
    df = pd.DataFrame(columns, index=indexes)
    df_0 = df.loc[:, (df != 0).any(axis=0)]  # убирает Столбцы с 0 значениями
    df_compact = df_0.loc[:, (df_0 != '0').any(axis=0)]  # если числа в виде строк
    return df_compact

def check_enough_funds(exchange):
    balance = get_balance(exchange)
    currencies = SYMBOL.split('/')
    base_curr = currencies[0]
    quote_curr = currencies[1]
    raises = []
    if base_curr in balance:
        if balance[base_curr]['free'] < VOLUME_BASE:
            raises.append(f'{base_curr} | Свободных Средств МЕНЬШЕ чем Зарезервировано')
    else:
        raises.append(f'{base_curr} | Нет средств')
    if quote_curr in balance:
        if balance[quote_curr]['free'] < VOLUME_QUOTE:
            raises.append(f'{quote_curr} | Свободных Средств МЕНЬШЕ чем Зарезервировано')
    else:
        raises.append(f'{quote_curr} | Нет средств')
    if len(raises):
        raise Exception(raises)

def get_price_levels(start_price, step_price):
    levels = {}
    levels['ask_2'] = round(start_price + 0.01 * LEVEL_2slab * start_price, step_price)
    levels['ask_1'] = round(start_price + 0.01 * LEVEL_1slab * start_price, step_price)
    levels['ask_carrot'] = round(start_price + 0.01 * MIN_SPRED * start_price, step_price)
    levels['bid_2'] = round(start_price - 0.01 * LEVEL_2slab * start_price, step_price)
    levels['bid_1'] = round(start_price - 0.01 * LEVEL_1slab * start_price, step_price)
    levels['bid_carrot'] = round(start_price - 0.01 * MIN_SPRED * start_price, step_price)
    return levels

def get_amounts(price_levels, step_volume):
    check_part_volume()
    amounts = {}
    amounts['ask_1'] = round(0.01 * PART_1slab * VOLUME_BASE, step_volume)
    amounts['ask_2'] = round(0.01 * PART_2slab * VOLUME_BASE, step_volume)
    amounts['ask_carrot'] = VOLUME_BASE - amounts['ask_1'] - amounts['ask_2']
    amounts['bid_1'] = round(0.01 * PART_1slab * VOLUME_QUOTE / price_levels['bid_1'], step_volume)
    amounts['bid_2'] = round(0.01 * PART_2slab * VOLUME_QUOTE / price_levels['bid_2'], step_volume)
    amounts['bid_carrot'] = round(0.01 * PART_carrot * VOLUME_QUOTE / price_levels['bid_carrot'], step_volume)
    return amounts

def check_part_volume():
    if (PART_carrot + PART_1slab + PART_2slab) != 100:
        raise Exception(f'Неверно заданы Доли Используемых средств. | (PART_carrot + PART_1slab + PART_2slab) Должна = 100')

def create_orders_1(exchange, price_levels, amounts):
    sell_order = exchange.create_order(SYMBOL, type='limit', side='sell', amount=amounts['ask_1'], price=price_levels['ask_1'])
    buy_order = exchange.create_order(SYMBOL, type='limit', side='buy', amount=amounts['bid_1'], price=price_levels['bid_1'])
    # Скинуть данные в Базу Данных
    # sleep(SLEEP_1slab)
    return (sell_order, buy_order)

def create_orders_2(exchange, price_levels, amounts):
    sell_order = exchange.create_order(SYMBOL, type='limit', side='sell', amount=amounts['ask_2'], price=price_levels['ask_2'])
    buy_order = exchange.create_order(SYMBOL, type='limit', side='buy', amount=amounts['bid_2'], price=price_levels['bid_2'])
    # Скинуть данные в Базу Данных
    # sleep(SLEEP_1slab)
    return (sell_order, buy_order)

def create_orders_carrot(exchange, price_levels, amounts):



    sell_order = exchange.create_order(SYMBOL, type='limit', side='sell', amount=amounts['ask_2'], price=price_levels['ask_2'])
    buy_order = exchange.create_order(SYMBOL, type='limit', side='buy', amount=amounts['bid_2'], price=price_levels['bid_2'])
    # Скинуть данные в Базу Данных
    # sleep(SLEEP_1slab)
    return (sell_order, buy_order)






def main():

    # Инициализация.
    exchange = connect_exchange()

    # Проверка. Достаточно ли средств:
    check_enough_funds(exchange)

    # Стартовая Цена от которой будут определять уровни и Количество Знаков после Запятой для Цен и Объемов
    start_price, step_price, step_volume = get_params_symbol(exchange)

    # Уровни Плит и Старта Приманки
    price_levels = get_price_levels(start_price, step_price)

    # Объемы (суммарный для Приманки) Ордеров
    amounts = get_amounts(price_levels, step_volume)

    # Ордера 1 Плиты
    orders_1 = create_orders_1(exchange, price_levels, amounts)

    # Ордера 2 Плиты

    # Ордера Приманки

    # ---------------------------------------------------------------------------------------
    # Мониторинг
    print(f'Стартовая Цена: {start_price} | Шаг Цены: {step_price} | Шаг Объема: {step_volume}')
    print(f'Уровни Цен:\n{pd.DataFrame.from_dict(price_levels, orient="index").transpose()}')
    print(f'Объемы:\n{pd.DataFrame.from_dict(amounts, orient="index").transpose()}')



# ---- RUN -----------------------------------------------------------------------------------
main()