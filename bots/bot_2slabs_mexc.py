import ccxt                     # Коннектор к Бирже
import pandas as pd             # Объекты DataFrame
import sqlite3 as sq            # Работа с БД
from typing import Literal      # Создание Классов Перечислений
from time import sleep, time    # Создание технологических Пауз
import random                   # Случайные значения
import json

from config_2slabs_mexc import *
from data_bases.path_to_base import DATABASE

pd.options.display.width= None # Отображение Таблицы на весь Экран
pd.options.display.max_columns= 20 # Макс Кол-во Отображаемых Колонок
# pd.options.display.float_format = '{:.6f}'.format # Формат отображения Чисел float

dividing_line = '-------------------------------------------------------------------------------'
double_line =   '==============================================================================='
order_table = 'orders_2slabs_mexc'
bot_name = 'bot_2slabs_mexc'
status_table = 'BotStatuses'
LevelType = Literal['slab_1', 'slab_2', 'carrots']
PartType = Literal['slab_1', 'slab_2', 'carrots', 'total']

def get_apikeys(account_name):
    with sq.connect(DATABASE) as connect:
        connect.row_factory = sq.Row  # Строки записей в виде dict {}. По умолчанию - кортежи turple ()
        curs = connect.cursor()
        curs.execute(f"SELECT apiKey, secret FROM Apikeys WHERE account LIKE '{account_name}' AND name LIKE 'Info'")
        keys = curs.fetchone()
        return {'apiKey': keys['apikey'], 'secret': keys['secret']}

def connect_exchange():
    apikeys = get_apikeys(ACCOUNT)
    trade_mode = get_trade_mode(ACCOUNT)
    try:
        exchange = ccxt.mexc(apikeys)
        if trade_mode == 'test': exchange.set_sandbox_mode(True)
        exchange.load_markets()
        return exchange
    except Exception as error:  # проверка на подключение
        raise print(error)

def get_balance(exchange):
    balance = exchange.fetch_balance()
    indexes = ['free', 'used', 'total']
    columns = [balance['free'], balance['used'], balance['total']]
    df = pd.DataFrame(columns, index=indexes)
    # df = df.astype(float)
    df_compact = df.loc[:, (df != 0).any(axis=0)]  # убирает Столбцы с 0 значениями
    return df_compact

def get_trade_mode(account_name):
    with sq.connect(DATABASE) as connect:
        curs = connect.cursor()
        curs.execute(f"SELECT type FROM Accounts WHERE name LIKE '{account_name}'")
        mode = curs.fetchone()[0]
        return mode

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

def get_accuracy(arg: list):
    accuracy = []
    for value in arg:
        value_str = str(value)
        if '.' in value_str:
            accuracy.append(len(value_str.split('.')[1]))
        else:
            accuracy.append(0)
    max_accuracy = max(accuracy)
    return max_accuracy

def get_params_symbol(exchange):
    try:
        data = exchange.fetch_ticker(SYMBOL)
        step_price = get_accuracy([data['open'], data['close'], data['high'], data['low']])
        step_volume = get_accuracy([data['bidVolume'], data['askVolume'], data['baseVolume']])
        start_price = round(((data['ask'] + data['bid']) / 2), step_price)
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
        curs.execute(f"INSERT INTO {order_table} VALUES(?, ?, ?, ?, ?, ?, ?)",
        (order['id'], order['symbol'], order['type'], order['side'], order['amount'], order['price'], name))


# def cancel_orders_exchange(exchange, name:LevelType):
#     id_orders = get_id_orders_sql(name)
#     for id in id_orders:
#         try:
#             exchange.cancel_order(id=id)
#             sleep(1)
#         except Exception as error:
#             print(f'Нет Ордера с id: {id} | {error}')
#
# def synchronize_orders(exchange, name:LevelType):
#     # Ордера (ID) с необходимым именем в БД
#     sql_id_orders = get_id_orders_sql(name)
#     if not len(sql_id_orders):
#         print(f'В БД НЕТ ордеров с именем: {name}')
#         return None
#
#     # Все Открытые Ордера (ID)
#     opened_orders = exchange.fetch_orders(SYMBOL)['result']
#
#     opened_id_orders = []
#     if not opened_orders['count']:
#         print(f'НЕТ ОТКРЫТЫХ ордеров')
#     else:
#         for order in opened_orders['orders']:
#             opened_id_orders.append(str(order['id'])) # int ?
#     print(f'Список ордеров в БД: {sql_id_orders}')
#     print(f'Список ОТКРЫТЫХ ордеров: {opened_id_orders}')
#
#     # Формимрование Списка Ордеров на Удаление из БД (в Базе есть а на Бирже Отсутствуют (Исполнены или что-то другое))
#     id_for_delete = []
#     for id in sql_id_orders:
#         if id not in opened_id_orders:
#             id_for_delete.append(id)
#
#     # Удаление Ордеров из БД
#     if len(id_for_delete):
#         with sq.connect(DATABASE) as connect:
#             curs = connect.cursor()
#             # ids = ','.join(map(str, id_for_delete))
#             ids = '\', \''.join(id_for_delete)
#             ids = '\'' + ids + '\''
#             curs.execute(f"DELETE FROM {order_table} WHERE id IN ({ids})")
#
#     return True
#
# def cancel_orders(exchange, name:LevelType):
#     sync = synchronize_orders(exchange, name)
#     if not sync:
#         return None
#     cancel_orders_exchange(exchange, name)
#     synchronize_orders(exchange, name)

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
        sell_order = exchange.create_order(SYMBOL, type='limit', side='sell', amount=ask_amount, price=ask_price)
        buy_order = exchange.create_order(SYMBOL, type='limit', side='buy', amount=bid_amount, price=bid_price)
        # Скинуть данные в Базу Данных
        write_order_sql(sell_order, name)
        write_order_sql(buy_order, name)
        return (sell_order, buy_order)
    except Exception as error:
        print(error)

def get_id_orders_sql(name:LevelType=None) -> list:
    with sq.connect(DATABASE) as connect:
        curs = connect.cursor()
        if name: curs.execute(f"SELECT id FROM {order_table} WHERE name LIKE '{name}'")
        else: curs.execute(f"SELECT id FROM {order_table}")
        ids = []
        for select in curs:
            ids.append(select[0])
        return ids

def get_id_order_exchange(exchange):
    open_orders = exchange.fetch_open_orders(SYMBOL)
    ids = []
    for order in open_orders:
        ids.append(order['id'])
    return ids

def delete_old_id_sql(old_ids:list):
    with sq.connect(DATABASE) as connect:
        curs = connect.cursor()
        # ids = ','.join(map(str, id_for_delete))
        ids = '\', \''.join(old_ids)
        curs.execute(f"DELETE FROM {order_table} WHERE id IN ('{ids}')")
    print(f'Из БД удалены Ордера: {old_ids}')

def cancel_orders_exchange(exchange, name:LevelType):
    id_orders = get_id_orders_sql(name)
    if not len(id_orders): return None
    for id in id_orders:
        try:
            exchange.cancel_order(id=id)
            print(f'Из Биржи Удален Ордер: {id}')
            sleep(1)
        except Exception as error:
            print(f'Нет Ордера с id: {id} | {error}')


def synchronize_orders(exchange, name:LevelType):
    sql_ids = get_id_orders_sql(name)
    exchange_ids = get_id_order_exchange(exchange)
    old_ids = []
    for id in sql_ids:
        if id not in exchange_ids:
            old_ids.append(id)
    if len(old_ids):
        delete_old_id_sql(old_ids) # Удалить неактуальные



def cancel_orders(exchange, name:LevelType):
    if not len(get_id_orders_sql(name)):
        print(f'{name} | Ордера ранее не выставлялись')
        return None
    while len(get_id_orders_sql(name)):
        synchronize_orders(exchange, name)
        cancel_orders_exchange(exchange, name)







def main():
    # Инициализация.
    exchange = connect_exchange()  # Соединение с Биржей
    print(f'Баланс Аккаунта:\n{get_balance(exchange)}\n{dividing_line}')  # Баланс аккаунта
    check_enough_funds(exchange)  # Проверка. Достаточно ли Общих средств:

    # i = 1
    # while get_bot_status_sql() == 'Run':
    #     ---------------------------------------------------------------------------------------
    #     print(f'{double_line}\nЦИКЛ: {i}\n{double_line}')
    #     start_time = time()

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
    cancel_orders(exchange, 'slab_1')  # удаляю ордера из предыдущый итерации
    # sleep(1)  # Необходиа пауза, иначе Биржа не успевает дать актуальную инфу по балансу
    check_enough_funds(exchange, 'slab_1')  # Проверка. Достаточно ли средств под эти Ордера:
    orders_1 = create_orders_Level(exchange, price_levels, amounts, name='slab_1')  # выставляю свежие ордера
    print(f'Выставлены Ордера 1-й уровень Плиты:')
    for order in orders_1:
        print(
            f"id: {order['id']} | {order['symbol']} | {order['type']} | {order['side']} | amount : {order['amount']} | price: {order['price']}")
    print(dividing_line)
    sleep(SLEEP_Level)
    #
    # # Ордера 2 Плиты
    # cancel_orders(exchange, 'slab_2')  # удаляю ордера из предыдущый итерации
    # sleep(1)  # Необходиа пауза, иначе Биржа не успевает дать актуальную инфу по балансу
    # check_enough_funds(exchange, 'slab_2')  # Проверка. Достаточно ли средств под эти Ордера:
    # orders_2 = create_orders_Level(exchange, price_levels, amounts, name='slab_2')  # выставляю свежие ордера
    # print(f'Выставлены Ордера 2-й уровень Плиты:')
    # for order in orders_2:
    #     print(
    #         f"id: {order['id']} | {order['symbol']} | {order['type']} | {order['side']} | amount : {order['quantity']} | price: {order['price']}")
    # print(dividing_line)
    # sleep(SLEEP_Level)
    #
    # # Ордера Приманки
    # cancel_orders(exchange, 'carrots')  # удаляю ордера из предыдущый итерации
    # sleep(1)  # Необходиа пауза, иначе Биржа не успевает дать актуальную инфу по балансу
    # carrots = create_orders_carrot(exchange, price_levels, amounts, step_price, step_volume)
    # print(f'Выставлены Ордера-Приманки:')
    # for order in carrots['sell_carrots']:
    #     print(
    #         f"id: {order['id']} | {order['symbol']} | {order['type']} | {order['side']} | amount : {order['quantity']} | price: {order['price']}")
    # for order in carrots['buy_carrots']:
    #     print(
    #         f"id: {order['id']} | {order['symbol']} | {order['type']} | {order['side']} | amount : {order['quantity']} | price: {order['price']}")
    # print(dividing_line)
    # sleep(SLEEP_Level)

    # finish_time = time()
    # print(f'Выполнено за: {start_time - finish_time} сек.')
    # i += 1
    # # ---------------------------------------------------------------------------------------

    # match get_bot_status_sql():
    #     case 'Stop':
    #         cancel_orders(exchange, name=None)
    #     case 'Pause':
    #         pass
    #     case _:
    #         pass


# ---- RUN -----------------------------------------------------------------------------------

main()
