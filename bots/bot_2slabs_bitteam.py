import pandas as pd
import sqlite3 as sq
from time import sleep
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

def choose_volumes(part_volume='total'):
    match part_volume:
        case 'total':
            V_Base = VOLUME_BASE
            V_Quote = VOLUME_QUOTE
        case 'carrots':
            V_Base = 0.01* PART_carrot * VOLUME_BASE
            V_Quote = 0.01 * PART_carrot * VOLUME_QUOTE
        case 'slabe_1':
            V_Base = 0.01 * PART_1slab * VOLUME_BASE
            V_Quote = 0.01 * PART_1slab * VOLUME_QUOTE
        case 'slabe_2':
            V_Base = 0.01 * PART_2slab * VOLUME_BASE
            V_Quote = 0.01 * PART_2slab * VOLUME_QUOTE
    return {'V_Base': V_Base, 'V_Quote': V_Quote}

def check_enough_funds(exchange, part_volume='total'):
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

def write_order_sql(order, name):
    with sq.connect(DATABASE) as connect:
        curs = connect.cursor()
        # "INSERT INTO orders VALUES(?, (SELECT name FROM pairs WHERE id=?), ?, ?, ?, ?)"
        curs.execute(f"""INSERT INTO {order_table} VALUES(?, ?, ?, ?, ?, ?, ?)""",
        (order['id'], order['symbol'], order['type'], order['side'], order['quantity'], order['price'], name))

def get_id_orders_sql(name):
    with sq.connect(DATABASE) as connect:
        curs = connect.cursor()
        curs.execute(f"""SELECT id FROM {order_table} WHERE name LIKE ?""", (name,))
        ids = []
        for select in curs:
            ids.append(select[0])
        return ids

def cancel_orders_exchange(exchange, name):
    id_orders = get_id_orders_sql(name)
    for id in id_orders:
        try:
            exchange.cancel_order(id=id)
        except Exception as error:
            print(f'Нет Ордера с id: {id} | {error}')

def synchronize_orders(exchange, name):
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
            curs.execute(f"DELETE FROM orders_2slabs WHERE id IN ({ids})")

    return True

def cancel_orders(exchange, name):
    sync = synchronize_orders(exchange, name)
    if not sync:
        return None
    cancel_orders_exchange(exchange, name)
    synchronize_orders(exchange, name)


def create_orders_1(exchange, price_levels, amounts):
    name = 'slabe_1'
    sell_order = exchange.create_order(SYMBOL, type='limit', side='sell', amount=amounts['ask_1'], price=price_levels['ask_1'])['result']
    sell_order['symbol'] = SYMBOL
    buy_order = exchange.create_order(SYMBOL, type='limit', side='buy', amount=amounts['bid_1'], price=price_levels['bid_1'])['result']
    buy_order['symbol'] = SYMBOL
    # Записываю данные в Базу Данных
    write_order_sql(sell_order, name)
    write_order_sql(buy_order, name)
    return (sell_order, buy_order)

def main():

    # Инициализация.
    exchange = connect_exchange() # Соединение с Биржей
    print(f'Баланс Аккаунта:\n{get_balance(exchange)}\n{dividing_line}') # Баланс аккаунта
    # check_enough_funds(exchange) # Проверка. Достаточно ли Общих средств:

    # # while True:
    # start_time = time()
    # # # Предварительно Удаляю Ранее выставленные Ордера
    # # exchange.cancel_all_orders(SYMBOL)

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
    cancel_orders(exchange, 'slabe_1') # удаляю ордера из предыдущый итерации
    check_enough_funds(exchange, 'slabe_1') # Проверка. Достаточно ли средств под эти Ордера:
    orders_1 = create_orders_1(exchange, price_levels, amounts) # выставляю свежие ордера
    print(f'Выставлены Ордера 1-й уровень Плиты:')
    for order in orders_1:
        print(f"id: {order['id']} | {order['symbol']} | {order['type']} | {order['side']} | amount : {order['quantity']} | price: {order['price']}")
    print(dividing_line)
    # sleep(3)
    #
    # # Ордера 2 Плиты
    # cancel_orders(exchange, 'slabe_2')
    # # check_enough_funds(exchange) # Проверка. Достаточно ли средств под эти Ордера: ПЕРЕДЕЛАТЬ!
    # orders_2 = create_orders_2(exchange, price_levels, amounts)
    # sleep(4)
    #
    # # Ордера Приманки
    # cancel_orders(exchange, 'carrots')
    # # check_enough_funds(exchange) # Проверка. Достаточно ли средств под эти Ордера: ПЕРЕДЕЛАТЬ!
    # carrots = create_orders_carrot(exchange, price_levels, amounts, step_price, step_volume)
    # sleep(2)
    #
    # # ---------------------------------------------------------------------------------------
    # # Передвинуть перед выставлением Ордеров!
    # # Мониторинг

    # print(f'---------------------------------------------------------------------')
    #
    # print(f'Выставлены Ордера 2-й уровень Плиты:')
    # for order in orders_2:
    #     print(f"id: {order['id']} | {order['symbol']} | {order['type']} | {order['side']} | amount : {order['amount']} | price: {order['price']} | status: {order['status']}")
    # print(f'---------------------------------------------------------------------')
    # print(f'Выставлены Ордера-Приманки:')
    # for order in carrots['sell_carrots']:
    #     print(f"id: {order['id']} | {order['symbol']} | {order['type']} | {order['side']} | amount : {order['amount']} | price: {order['price']} | status: {order['status']}")
    # for order in carrots['buy_carrots']:
    #     print(f"id: {order['id']} | {order['symbol']} | {order['type']} | {order['side']} | amount : {order['amount']} | price: {order['price']} | status: {order['status']}")
    # finish_time = time()
    # print(f'Выполнено за: {start_time - finish_time} сек.')

# ---- RUN -----------------------------------------------------------------------------------

main()