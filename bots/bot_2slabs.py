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

def get_num_orders_carrot(amounts, price_levels):
    amount = amounts['ask_carrot'] * price_levels['ask_carrot']
    slice = amount / NUM_carrots
    if slice >= MIN_AMOUNT:
        return NUM_carrots
    else:
        return int(amount / MIN_AMOUNT)


def get_slices(num_carrot, amounts, step_volume):
    slice = round(amounts['ask_carrot'] / num_carrot, step_volume)
    ask_slices = []
    bid_slices = []
    for i in range(1, num_carrot):
      ask_slices.append(round(random.randrange(90, 110) * 0.01 * slice, step_volume))
      bid_slices.append(round(random.randrange(90, 110) * 0.01 * slice, step_volume))
    ask_subsum = sum(ask_slices)
    bid_subsum = sum(bid_slices)
    ask_slices.append(round(amounts['ask_carrot'] - ask_subsum, step_volume))
    bid_slices.append(round(amounts['ask_carrot'] - ask_subsum, step_volume))
    return {'ask_slices': ask_slices, 'bid_slices': bid_slices}


def get_carrot_prices(num_carrot, price_levels, step_price):
    ask_prices = [price_levels['ask_carrot']]
    bid_prices = [price_levels['bid_carrot']]
    delta = (price_levels['ask_1'] - price_levels['ask_carrot']) / num_carrot
    for i in range(1, num_carrot):
        ask_delta = round(random.uniform(0.8 * delta, 1.2 * delta), step_price)
        bid_delta = round(random.uniform(0.8 * delta, 1.2 * delta), step_price)
        ask_prices.append(round(ask_prices[i-1] + ask_delta, step_price))
        bid_prices.append(round(bid_prices[i-1] - bid_delta, step_price))
    return {'ask_prices': ask_prices, 'bid_prices': bid_prices}




def create_orders_carrot(exchange, price_levels, amounts, step_price, step_volume):
    num_carrot = get_num_orders_carrot(amounts, price_levels)
    carrot_slices = get_slices(num_carrot, amounts, step_volume)
    carrot_prices = get_carrot_prices(num_carrot, price_levels, step_price)

    sell_carrots = []
    buy_carrots = []
    for i in range(num_carrot-1):
        sell_order = exchange.create_order(SYMBOL, type='limit', side='sell', amount=carrot_slices['ask_slices'][i], price=carrot_prices['ask_prices'][i])
        sell_carrots.append(sell_order)
        buy_order = exchange.create_order(SYMBOL, type='limit', side='buy', amount=carrot_slices['bid_slices'][i], price=carrot_prices['bid_prices'][i])
        buy_carrots.append(buy_order)
    print(f'Приманки-Морковки.  -----------------------------------')
    print(f'Количество на сторону: {num_carrot}')
    print(f'Объемы в Базовой валюте: {carrot_slices}')
    print(f"Примерные Объемы в Котирующей валюте (обычно USDT): | "
          f"МАКС: {round(max(carrot_slices['ask_slices'])*price_levels['ask_1'], step_volume)} | "
          f"МИН: {round(min(carrot_slices['bid_slices'])*price_levels['bid_1'], step_volume)}")
    print(f'Уровни Цен: {carrot_prices}')
    print(f'--------------------------------------------------------')

    # # Скинуть данные в Базу Данных
    # # sleep(3)
    return {'sell_carrots': sell_carrots, 'buy_carrots': buy_carrots}

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
    # orders_1 = create_orders_1(exchange, price_levels, amounts)

    # Ордера 2 Плиты

    # Ордера Приманки
    carrots = create_orders_carrot(exchange, price_levels, amounts, step_price, step_volume)


    # ---------------------------------------------------------------------------------------
    # Мониторинг
    print(f'Стартовая Цена: {start_price} | Шаг Цены: {step_price} | Шаг Объема: {step_volume}')
    print(f'--------------------------------------------------------')
    print(f'Уровни Цен:\n{pd.DataFrame.from_dict(price_levels, orient="index").transpose()}')
    print(f'--------------------------------------------------------')
    print(f'Объемы:\n{pd.DataFrame.from_dict(amounts, orient="index").transpose()}')
    print(f'--------------------------------------------------------')
    # print(f'Приманки:\n{carrots}', sep='\n')



# ---- RUN -----------------------------------------------------------------------------------
main()