import streamlit as st                          # Библиотека Компоновщик Страниц Интерфейся
import sqlite3 as sq                            # Библиотека  Работа с БД
import pandas as pd                             # Преобразовать Словари в Таблицы
# import subprocess                               # Запуск внешних скриптов
# import psutil                                   # Инфо и Управление запущенными процессами
# import os, signal                               # Запуск внешних скриптов / Куски кода в комментах
import ccxt
from data_bases.path_to_base import DATABASE

# В терминале набрать:
# streamlit run app.py

def get_accounts():
    with sq.connect(DATABASE) as connect:
        connect.row_factory = sq.Row  # Строки записей в виде dict {}. По умолчанию - кортежи turple ()
        curs = connect.cursor()

        curs.execute("""SELECT 
account, 
apikey as apiKey, 
secret, 
Accounts.exchange,
Accounts.type 
FROM Apikeys 
JOIN Accounts ON Accounts.name == Apikeys.account
WHERE Apikeys.name LIKE 'Info'""")
        return curs.fetchall()

def connect_exchange(account):
    apikeys = {'apiKey': account['apiKey'], 'secret': account['secret']}
    match account['exchange']:
        case 'Binance':
            exchange = ccxt.binance(apikeys)
            if account['type'] == 'test':
                exchange.set_sandbox_mode(True)
        case 'BitTeam':
            exchange = None
        case 'Bybit':
            exchange = ccxt.bybit(apikeys)
        case 'Mexc':
            exchange = ccxt.mexc(apikeys)
        case 'Gate_io':
            exchange = ccxt.gateio(apikeys)
        case _:
            exchange = None

    # match account['exchange']:
    #     case 'Binance' | 'Bybit' | 'Mexc' | 'Gate_io':
    #         exchange.load_markets()

    return exchange

def get_balance(exchange):
    if not exchange:
        return None
    try:
        balance = exchange.fetch_balance()
        indexes = ['free', 'used', 'total']
        columns = [balance['free'], balance['used'], balance['total']]
        df = pd.DataFrame(columns, index=indexes)
        df_compact = df.loc[:, (df != 0).any(axis=0)]
        return df_compact
    except Exception as error:
        return pd.DataFrame({'ERROR': error.args}) # , df_compact.columns

def get_orders(exchange):
    if not exchange:
        return None
    try:
        orders = exchange.fetch_orders(symbol='ETH/USDT') # без символа торгуемой пары большинство бирж не дают данные
        return pd.DataFrame(orders)
    except Exception as error:
        return pd.DataFrame({'ERROR': error.args})


st.set_page_config(layout="wide") # Вся страница вместо узкой центральной колонки

st.header('Торговые Аккаунты', anchor=False, divider='red')
st.header('')

with st.form('Accounts'):
    button = st.form_submit_button('Получить Балансы по всем Аккаунтам')
    if button:
        accounts = get_accounts()
        if len(accounts) == 0:
            st.write("В Базе Данных нет ни одного ключа для данных Целей")
            st.stop()
        columnA, columnB, columnC, columnD = st.columns(4)
        i = 1
        for account in accounts:
            match i % 4:
                case 1: # 1 Колонка
                    name_column = 'columnA'
                case 2: # 2 Колонка
                    name_column = 'columnB'
                case 3: # 3 Колонка
                    name_column = 'columnC'
                case 0: # 4 Колонка
                    name_column = 'columnD'

            # st.markdown(f"<h4>{account['account']}</h4>", unsafe_allow_html=True)
            name_account = f"<h4>{account['account']}</h4>"
            func = f"{name_column}.markdown('{name_account}', unsafe_allow_html=True)"
            eval(func)

            exchange = connect_exchange(account)

            balance = get_balance(exchange)
            func = f"{name_column}.dataframe(balance)"
            eval(func)

            # orders = get_orders(exchange)
            # st.dataframe(orders)
            i += 1
            eval(f"{name_column}.markdown('---')" )


