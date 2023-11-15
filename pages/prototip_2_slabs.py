import streamlit as st                          # Библиотека Компоновщик Страниц Интерфейся
import sqlite3 as sq                            # Библиотека  Работа с БД
import pandas as pd                             # Преобразовать Словари в Таблицы
# import subprocess                               # Запуск внешних скриптов
# import psutil                                   # Инфо и Управление запущенными процессами
# import os, signal                               # Запуск внешних скриптов / Куски кода в комментах
import ccxt
from data_bases.path_to_base import DATABASE
from connectors.bitteam import BitTeam
st.set_page_config(layout="wide") # Вся страница вместо узкой центральной колонки

# В терминале набрать:
# streamlit run app.py

# 1. Выбрать Торговый Аккаунт (ключи)
# 2. Узнать (Дать Инфу) о Состояние Счета.
# 3. Задать Торгуемую Пару
#   Получить Общ Инфу по паре (макс, мин, объемы, и тд - что конкретно интересует.).
# 4. Задать Объем Используемых Средств: Free / Used / Total / abs / %proc
#   Base Currency
#   Quote Currency.
# 5. Задать Уровень 1-й Опорной Плиты
#   % от Текущих цен
#   max, min за 00 дней
#   Статичное Пользоватальское Значение.
# 6. Задать Уровень 2-й Опорной Плиты
#   % от Текущих цен
#   max, min за 00 дней
#   Статичное Пользоватальское Значение.
# 7. Распределить Средства: 1й Уровень / 2й Уровень / Приманка
# 8. Частота Обновления Плит. (1й ур / 2ур)

def get_all_accounts():
    with sq.connect(DATABASE) as connect:
        connect.row_factory = sq.Row  # Строки записей в виде dict {}. По умолчанию - кортежи turple ()
        curs = connect.cursor()
        curs.execute("""SELECT * FROM Accounts""")
        return curs.fetchall()

def get_apikeys(account_name):
    with sq.connect(DATABASE) as connect:
        connect.row_factory = sq.Row  # Строки записей в виде dict {}. По умолчанию - кортежи turple ()
        curs = connect.cursor()
        curs.execute("""SELECT apiKey, secret FROM Apikeys WHERE account LIKE ? AND name LIKE 'Info' LIMIT 1""", (account_name,))
        keys = curs.fetchone()
        return {'apiKey': keys['apikey'], 'secret': keys['secret']}

@st.cache_data
def connect_exchange(account_name):
    apikeys = get_apikeys(account_name)
    match account_exchange:
        case 'Binance':
            exchange = ccxt.binance(apikeys)
            if account_type == 'test':
                exchange.set_sandbox_mode(True)
        case 'BitTeam':
            exchange = BitTeam(apikeys)
        case 'Bybit':
            exchange = ccxt.bybit(apikeys)
        case 'Mexc':
            exchange = ccxt.mexc(apikeys)
        case 'Gate_io':
            exchange = ccxt.gateio(apikeys)
        case _:
            exchange = None
    match account_exchange:
        case 'Binance' | 'Bybit' | 'Mexc' | 'Gate_io':
            exchange.load_markets()
    return exchange

def get_balance_account():
    if not account_name:
        return None
    try:
        exchange = connect_exchange(account_name)
        balance = exchange.fetch_balance()
        indexes = ['free', 'used', 'total']
        columns = [balance['free'], balance['used'], balance['total']]
        df = pd.DataFrame(columns, index=indexes)
        df_0 = df.loc[:, (df != 0).any(axis=0)] # убирает Столбцы с 0 значениями
        df_compact = df_0.loc[:, (df_0 != '0').any(axis=0)] # если числа в виде строк
    except Exception as error:
        # return pd.DataFrame({'ERROR': error.args}) # , df_compact.columns
        df_compact = pd.DataFrame({'ERROR': error.args})
    return df_compact

def get_balance():
    if st.session_state.balance:
        balance = get_balance_account()
        return balance

def get_binance_symbol_info(data):
    return None

def get_bitteam_symbol_info(data):
    data_ = data['result']['pair']
    info = {'High 24h': data_['highPrice24'],
            'Low 24h': data_['lowPrice24'],
            'last BUY': float(data_['lastBuy']),
            'last SELL': float(data_['lastSell']),
            'change 24h': float(data_['change24']),
            'volume 24h Base': data_['volume24'],
            'volume 24h Quote': data_['quoteVolume24'],
            'volume 24h USD': data_['volume24USD'],
            'amount ASKS': float(data_['quantities']['asks']),
            'amount BIDS': float(data_['quantities']['bids'])
    }
    return info


def get_symbol_info_exchange():
    if not symbol: return('Вы не выбрали Торгуемую Пару (Символ)')
    exchange = connect_exchange(account_name)
    data = exchange.fetch_ticker(symbol)
    match account_exchange:
        case 'Binance':
            info = get_binance_symbol_info(data)
        case 'BitTeam':
            info = get_bitteam_symbol_info(data)
        case 'Bybit':
            info = None
        case 'Mexc':
            info = None
        case 'Gate_io':
            info = None
        case _:
            info = None
    return info



def get_symbol_info():
    if st.session_state.symbol:
        info = get_symbol_info_exchange()
        return info
    pass





st.subheader('Прототип Интерфейта Торговой Стратегии "2 Опорных Плиты и Приманка"', anchor=False, divider='red')

marks = ['Step 1. Analys and Info', 'Step 2', 'Step 3', 'Step 4', 'Step 5']
tabs = st.tabs(marks)

with tabs[0]:
    accounts = pd.DataFrame(get_all_accounts(), columns=['account', 'exchange', 'type'])
    account_name = st.selectbox('Trade Account', options=accounts, index=None, placeholder="Select Trade Account...")
    account = accounts[accounts['account'] == account_name].reset_index()
    if account_name:
        account_exchange = account['exchange'][0]
        account_type = account['type'][0]
    else:
        account_exchange = 'не определена'
        account_type = 'не определен'
    st.markdown(f"Биржа: <b>{account_exchange}</b> || Режим <b>{account_type}</b>", unsafe_allow_html=True)
    toggle_balance = st.toggle('Таблица Баланса по Счету', on_change=get_balance, key='balance')
    st.write(get_balance())

    symbols = ['DEL/USDT', 'ETH/USDT', 'BTC/USDT', 'ATOM/USDT', 'XRP/USDT']
    symbol = st.selectbox('Symbol', options=symbols, index=None, placeholder="Select Trade Symbol...")
    toggle_symbol = st.toggle('Информация по Торговой Паре', on_change=get_symbol_info, key='symbol')
    # st.write(get_symbol_info())
    st.dataframe(get_symbol_info())




# 1. Выбрать Торговый Аккаунт (ключи)

