import sqlite3 as sq                                 # Работа с БД
import pandas as pd                                  # Объекты DataFrame
from typing import Literal                           # Создание Классов Перечислений
from time import sleep, time, localtime, strftime    # Создание технологических Пауз
import random                                        # Случайные значения
import seaborn as sns
from matplotlib import pyplot as plt
# import json

from connectors.bitteam import BitTeam # Коннектор API к Бирже BitTeam
from config_2slabs_bitteam import * # Конфигурационный Файл (Настраиваемые Параметры)
from data_bases.path_to_base import DATABASE

pd.options.display.width= None # Отображение Таблицы на весь Экран
pd.options.display.max_columns= 20 # Макс Кол-во Отображаемых Колонок
pd.options.display.float_format = '{:.6f}'.format # Формат отображения Чисел float
dividing_line = '-------------------------------------------------------------------------------------'
double_line =   '====================================================================================='
order_table = 'orders_neighbour_bitteam'
bot_name = 'bot_neighbour_bitteam'
status_table = 'BotStatuses'
LevelType = Literal['neighbour', 'carrots', None]
PartType = Literal['neighbour', 'carrots', 'total']

# 0. Найти Точность
# 1. Найти Среднюю цену
#
# 3. Стакан - найти Плиту
# 4. Присоседиться Плитой
# Найти 2ю Границу
# 5. Размазать на участке
#
# Пересчет:
# Стакан - плита осталась?
# Пауза
#
# Сместилась
# Пересчет на это смещение
#
# Нет Плит?
# Вопрос

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


def get_price_symbol(exchange, step_price):
    try:
        ticker = exchange.fetch_ticker(SYMBOL)['result']['pair']
        start_price = round(((float(ticker['asks'][0]['price']) + float(ticker['bids'][0]['price'])) / 2), step_price)
    except Exception as error:
        raise Exception(error)
    return start_price

def get_accuracy_symbol(exchange):
    try:
        ticker = exchange.fetch_ticker(SYMBOL)['result']['pair']['settings']
        step_price = int(ticker['price_view_min'])
        step_volume = int(ticker['lot_size_view_min'])
    except Exception as error:
        raise Exception(error)
    return (step_price, step_volume)

def get_slab(exchange):
    try:
        ticker = exchange.fetch_ticker(SYMBOL)['result']['pair']
    except Exception as error:
        raise Exception(error)
    asks = pd.DataFrame(ticker['asks']).astype(float)
    bids = pd.DataFrame(ticker['bids']).astype(float)
    asks.describe()
    # print('ASKS', asks, asks.describe(), asks.quantile(.618), asks.sum(), sep='\n')
    # print('BIDS', bids, bids.describe(), bids.quantile(.618), bids.sum(), sep='\n')
    # print('ASKS', asks, dividing_line, 'BIDS', bids, dividing_line, sep='\n')
    # print('ASKS', asks.describe(), dividing_line, 'BIDS', bids.describe(), sep='\n')

    print('ASKS', asks, dividing_line, 'BIDS', bids, dividing_line, sep='\n')
    print('ASKS', 'Golden Section:', asks.iloc[:, 1:].quantile(0.618), 'Mean:', asks.iloc[:, 1:].mean(), 'SUM', asks.iloc[:, 1:].sum(), dividing_line, sep='\n')
    print('BIDS', 'Golden Section:', bids.iloc[:, 1:].quantile(0.618), 'Mean:', bids.iloc[:, 1:].mean(), 'SUM', bids.iloc[:, 1:].sum(), dividing_line, sep='\n')


    fig = plt.figure(figsize=(12, 6), dpi=80) # figsize=(size_h, size_v)
    gs = fig.add_gridspec(1, 2)
    sns.set_theme(style="whitegrid")
    sns.axes_style("darkgrid")

    fig.add_subplot(gs[0, 0])
    sns.histplot(data=asks, x='amount', label="Asks", color="red", bins=20).set_title('ASKS')

    fig.add_subplot(gs[0, 1])
    sns.histplot(data=bids, x='amount', label="Bids", color="green", bins=20).set_title('BIDS')

    sns.despine(left=True, bottom=True, right=True, top=True)
    plt.show()


def main():
    # Инициализация
    exchange = connect_exchange()

    # Баланс в компактной Табличной Форме
    balance = get_balance(exchange)
    print(balance)

    # # Точность - Шаг Цен и Объемов по Торговой Паре
    # step_price, step_volume = get_accuracy_symbol(exchange)
    # print(f'{SYMBOL} | Шаг Цены: {step_price} | Шаг Объема: {step_volume}')
    #
    # # Текущая Цена:
    # askbid_price = get_price_symbol(exchange, step_price)
    # print(f'{SYMBOL} | Средняя Цена между лучшими Ask и Bid: {askbid_price}')

    # Уровень Соседа
    get_slab(exchange)







# ------------------------------------
main()