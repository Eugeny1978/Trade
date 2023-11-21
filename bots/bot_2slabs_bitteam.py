import pandas as pd
import sqlite3 as sq
from typing import Literal                      # Создание Классов Перечислений
from time import sleep, time
import random
import json
# import ccxt
# import multiprocessing as mp

from connectors.bitteam import BitTeam
from config_2slabs_bitteam import *
from data_bases.path_to_base import DATABASE

pd.options.display.width= None # Отображение Таблицы на весь Экран
pd.options.display.max_columns= 20 # Макс Кол-во Отображаемых Колонок
pd.options.display.float_format = '{:.6f}'.format # Формат отображения Чисел float
# pd.set_option('display.float_format', '{:.6f}'.format)
dividing_line = '-------------------------------------------------------------------------------'
order_table = 'orders_2slabs_bitteam'
LevelType = Literal['slab_1', 'slab_2', 'carrots']
PartType = Literal['slab_1', 'slab_2', 'carrots', 'total']

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
    df = df.astype(float)
    df_compact = df.loc[:, (df != 0).any(axis=0)]  # убирает Столбцы с 0 значениями
    # df_compact = df_0.loc[:, (df_0 != '0').any(axis=0)]  # если числа в виде строк
    return df_compact

def choose_volumes(part_volume:PartType):
    match part_volume:
        case 'total':
            V_Base = VOLUME_BASE
            V_Quote = VOLUME_QUOTE
        case 'carrots':
            V_Base = 0.01 * PART_carrot * VOLUME_BASE
            V_Quote = 0.01 * PART_carrot * VOLUME_QUOTE
        case 'slab_1':
            V_Base = 0.01 * PART_1slab * VOLUME_BASE
            V_Quote = 0.01 * PART_1slab * VOLUME_QUOTE
        case 'slab_2':
            V_Base = 0.01 * PART_2slab * VOLUME_BASE
            V_Quote = 0.01 * PART_2slab * VOLUME_QUOTE
    return {'V_Base': V_Base, 'V_Quote': V_Quote}

def check_enough_funds(exchange, part_volume:PartType='total'):
    balance = get_balance(exchange)
    currencies = SYMBOL.split('/')
    base_curr = currencies[0]
    quote_curr = currencies[1]
    raises = []
    volumes = choose_volumes(part_volume)
    if base_curr in balance:
        if balance[base_curr]['free'] < volumes['V_Base']:
            raises.append(f'{base_curr} | Свободных Средств МЕНЬШЕ чем Зарезервировано')
    else:
        raises.append(f'{base_curr} | Нет средств')
    if quote_curr in balance:
        if balance[quote_curr]['free'] < volumes['V_Quote']:
            raises.append(f'{quote_curr} | Свободных Средств МЕНЬШЕ чем Зарезервировано')
    else:
        raises.append(f'{quote_curr} | Нет средств')
    if len(raises):
        raise Exception(f'VOLUME {part_volume.upper()}: {raises}')

def get_params_symbol(exchange):
    try:
        data = exchange.fetch_ticker(SYMBOL)['result']['pair']
        step_price = int(data['settings']['price_view_min'])
        step_volume = int(data['settings']['lot_size_view_min'])
        start_price = round(((float(data['asks'][0]['price']) + float(data['bids'][0]['price'])) / 2), step_price)
    except Exception as error:
        raise Exception(error)
    return (start_price, step_price, step_volume)

def get_price_levels(start_price, step_price):
    levels = {}
    levels['ask_2'] = round(start_price + 0.01 * LEVEL_2slab * start_price, step_price)
    levels['ask_1'] = round(start_price + 0.01 * LEVEL_1slab * start_price, step_price)
    levels['ask_carrot'] = round(start_price + 0.01 * MIN_SPRED * start_price, step_price)
    levels['bid_carrot'] = round(start_price - 0.01 * MIN_SPRED * start_price, step_price)
    levels['bid_1'] = round(start_price - 0.01 * LEVEL_1slab * start_price, step_price)
    levels['bid_2'] = round(start_price - 0.01 * LEVEL_2slab * start_price, step_price)
    return levels

def get_amounts(price_levels, step_volume):
    check_part_volume()
    amounts = {}
    amounts['ask_2'] = round(0.01 * PART_2slab * VOLUME_BASE, step_volume)
    amounts['ask_1'] = round(0.01 * PART_1slab * VOLUME_BASE, step_volume)
    amounts['ask_carrot'] = VOLUME_BASE - amounts['ask_1'] - amounts['ask_2']
    amounts['bid_carrot'] = round(0.01 * PART_carrot * VOLUME_QUOTE / price_levels['bid_carrot'], step_volume)
    amounts['bid_1'] = round(0.01 * PART_1slab * VOLUME_QUOTE / price_levels['bid_1'], step_volume)
    amounts['bid_2'] = round(0.01 * PART_2slab * VOLUME_QUOTE / price_levels['bid_2'], step_volume)
    return amounts

def check_part_volume():
    if (PART_carrot + PART_1slab + PART_2slab) != 100:
        raise Exception(f'Неверно заданы Доли Используемых средств. | (PART_carrot + PART_1slab + PART_2slab) Должна = 100')

def write_order_sql(order, name:LevelType):
    with sq.connect(DATABASE) as connect:
        curs = connect.cursor()
        # "INSERT INTO orders VALUES(?, (SELECT name FROM pairs WHERE id=?), ?, ?, ?, ?)"
        curs.execute(f"""INSERT INTO {order_table} VALUES(?, ?, ?, ?, ?, ?, ?)""",
        (order['id'], order['symbol'], order['type'], order['side'], order['quantity'], order['price'], name))

def get_id_orders_sql(name:LevelType):
    with sq.connect(DATABASE) as connect:
        curs = connect.cursor()
        curs.execute(f"""SELECT id FROM {order_table} WHERE name LIKE ?""", (name,))
        ids = []
        for select in curs:
            ids.append(select[0])
        return ids

def cancel_orders_exchange(exchange, name:LevelType):
    id_orders = get_id_orders_sql(name)
    for id in id_orders:
        try:
            exchange.cancel_order(id=id)
        except Exception as error:
            print(f'Нет Ордера с id: {id} | {error}')

def synchronize_orders(exchange, name:LevelType):
    # Ордера (ID) с необходимым именем в БД
    sql_id_orders = get_id_orders_sql(name)
    if not len(sql_id_orders):
        print(f'В БД НЕТ ордеров с именем: {name}')
        return None

    # Все Открытые Ордера (ID)
    opened_orders = exchange.fetch_orders(SYMBOL)['result']

    opened_id_orders = []
    if not opened_orders['count']:
        print(f'НЕТ ОТКРЫТЫХ ордеров')
    else:
        for order in opened_orders['orders']:
            opened_id_orders.append(str(order['id'])) # int ?
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
            # ids = ','.join(map(str, id_for_delete))
            ids = '\', \''.join(id_for_delete)
            ids = '\'' + ids + '\''
            curs.execute(f"DELETE FROM {order_table} WHERE id IN ({ids})")

    return True

def cancel_orders(exchange, name:LevelType):
    sync = synchronize_orders(exchange, name)
    if not sync:
        return None
    cancel_orders_exchange(exchange, name)
    synchronize_orders(exchange, name)

def create_orders_Level(exchange, price_levels, amounts, name:LevelType):
    match name:
        case 'slab_1':
            ask_amount = amounts['ask_1']
            bid_amount = amounts['bid_1']
            ask_price = price_levels['ask_1']
            bid_price = price_levels['bid_1']
        case 'slab_2':
            ask_amount = amounts['ask_2']
            bid_amount = amounts['bid_2']
            ask_price = price_levels['ask_2']
            bid_price = price_levels['bid_2']
        case _:
            pass
    try:
        sell_order = exchange.create_order(SYMBOL, type='limit', side='sell', amount=ask_amount, price=ask_price)['result']
        sell_order['symbol'] = SYMBOL
        buy_order = exchange.create_order(SYMBOL, type='limit', side='buy', amount=bid_amount, price=bid_price)['result']
        buy_order['symbol'] = SYMBOL
        # Скинуть данные в Базу Данных
        write_order_sql(sell_order, name)
        write_order_sql(buy_order, name)
        return (sell_order, buy_order)
    except Exception as error:
        print(error)


def correct_num_orders_carrot(amounts, price_levels):
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
      ask_slices.append(round(random.uniform(0.8 * slice, 1.2 * slice), step_volume))
      bid_slices.append(round(random.uniform(0.8 * slice, 1.2 * slice), step_volume))
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
    num_carrot = correct_num_orders_carrot(amounts, price_levels)
    carrot_slices = get_slices(num_carrot, amounts, step_volume)
    carrot_prices = get_carrot_prices(num_carrot, price_levels, step_price)

    sell_carrots = []
    buy_carrots = []
    name = 'carrots'
    for i in range(num_carrot):
        sell_order = exchange.create_order(SYMBOL, type='limit', side='sell', amount=carrot_slices['ask_slices'][i], price=carrot_prices['ask_prices'][i])
        sell_carrots.append(sell_order)
        write_order_sql(sell_order, name) # Записываю Ордер в Базу Данных
        buy_order = exchange.create_order(SYMBOL, type='limit', side='buy', amount=carrot_slices['bid_slices'][i], price=carrot_prices['bid_prices'][i])
        buy_carrots.append(buy_order)
        write_order_sql(buy_order, name) # Записываю Ордер в Базу Данных
    print(f'Приманки-Морковки.  -------------------------------------------------')
    print(f'Количество на сторону: {num_carrot}')
    print(f'Объемы в Базовой валюте: {carrot_slices}')
    print(f"Примерные Объемы в Котирующей валюте (обычно USDT): | "
          f"МАКС: {round(max(carrot_slices['ask_slices'])*price_levels['ask_1'], step_volume)} | "
          f"МИН: {round(min(carrot_slices['bid_slices'])*price_levels['bid_1'], step_volume)}")
    print(f'Уровни Цен: {carrot_prices}')
    print(f'---------------------------------------------------------------------')

    return {'sell_carrots': sell_carrots, 'buy_carrots': buy_carrots}


def main():

    # Инициализация.
    exchange = connect_exchange() # Соединение с Биржей
    print(f'Баланс Аккаунта:\n{get_balance(exchange)}\n{dividing_line}') # Баланс аккаунта
    # check_enough_funds(exchange) # Проверка. Достаточно ли Общих средств:

    # # while True:
    start_time = time()

    # Стартовая Цена от которой будут определять уровни и Количество Знаков после Запятой для Цен и Объемов
    start_price, step_price, step_volume = get_params_symbol(exchange)
    print(f'Старт-Цена: {start_price} | Шаг Цен: {step_price} | Шаг Объемов: {step_volume}\n{dividing_line}')

    # Уровни Плит и Старта Приманки
    price_levels = get_price_levels(start_price, step_price)
    print(f'Уровни Цен:\n{pd.DataFrame.from_dict(price_levels, orient="index").transpose()}\n{dividing_line}')

    # Объемы (суммарный для Приманки) Ордеров
    amounts = get_amounts(price_levels, step_volume)
    print(f'Объемы:\n{pd.DataFrame.from_dict(amounts, orient="index").transpose()}\n{dividing_line}')

    # Ордера 1 Плиты
    cancel_orders(exchange, 'slab_1') # удаляю ордера из предыдущый итерации
    sleep(1) # Необходиа пауза, иначе Биржа не успевает дать актуальную инфу по балансу
    check_enough_funds(exchange, 'slab_1') # Проверка. Достаточно ли средств под эти Ордера:
    orders_1 = create_orders_Level(exchange, price_levels, amounts, name='slab_1') # выставляю свежие ордера
    print(f'Выставлены Ордера 1-й уровень Плиты:')
    for order in orders_1:
        print(f"id: {order['id']} | {order['symbol']} | {order['type']} | {order['side']} | amount : {order['quantity']} | price: {order['price']}")
    print(dividing_line)
    sleep(SLEEP_Level)

    # Ордера 2 Плиты
    cancel_orders(exchange, 'slab_2')  # удаляю ордера из предыдущый итерации
    sleep(1)  # Необходиа пауза, иначе Биржа не успевает дать актуальную инфу по балансу
    check_enough_funds(exchange, 'slab_2')  # Проверка. Достаточно ли средств под эти Ордера:
    orders_2 = create_orders_Level(exchange, price_levels, amounts, name='slab_2')  # выставляю свежие ордера
    print(f'Выставлены Ордера 2-й уровень Плиты:')
    for order in orders_2:
        print(f"id: {order['id']} | {order['symbol']} | {order['type']} | {order['side']} | amount : {order['quantity']} | price: {order['price']}")
    print(dividing_line)
    sleep(SLEEP_Level)

    # Ордера Приманки
    cancel_orders(exchange, 'carrots')  # удаляю ордера из предыдущый итерации
    sleep(1)  # Необходиа пауза, иначе Биржа не успевает дать актуальную инфу по балансу
    carrots = create_orders_carrot(exchange, price_levels, amounts, step_price, step_volume)
    print(f'Выставлены Ордера-Приманки:')
    for order in carrots['sell_carrots']:
        print(f"id: {order['id']} | {order['symbol']} | {order['type']} | {order['side']} | amount : {order['quantity']} | price: {order['price']}")
    for order in carrots['buy_carrots']:
        print(f"id: {order['id']} | {order['symbol']} | {order['type']} | {order['side']} | amount : {order['quantity']} | price: {order['price']}")
    print(dividing_line)
    sleep(SLEEP_Level)

    # ---------------------------------------------------------------------------------------
    finish_time = time()
    print(f'Выполнено за: {start_time - finish_time} сек.')

# ---- RUN -----------------------------------------------------------------------------------

main()