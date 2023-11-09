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


def get_account_names(accounts):
    account_names = []
    for account in accounts:
        account_names.append(account['account'])
    return account_names

# def get_tab_names(account_names):
#     tab_names = []
#     for name in account_names:
#         tab_names.append(f'tab_{name}')
#     return tab_names



st.set_page_config(layout="wide") # Вся страница вместо узкой центральной колонки

st.header('Торговые Аккаунты', anchor=False, divider='red')
st.header('')

with st.form('Accounts'):
    button = st.form_submit_button('Получить Информацию по Аккаунтам')
    if button:
        accounts = get_accounts()
        if len(accounts) == 0:
            st.write("В Базе Данных нет ни одного ключа для данных Целей")
            st.stop()
        account_names = get_account_names(accounts)
        tabs = st.tabs(account_names)

        i = 0
        for tab in tabs:
            tab.subheader(account_names[i])
            tab.markdown(f"Биржа: {accounts[i]['exchange']}")
            exchange = connect_exchange(accounts[i])
            balance = get_balance(exchange)
            tab.dataframe(balance)

            i += 1




