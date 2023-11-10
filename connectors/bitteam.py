# from api.request import Request               # Базовый Класс
import pandas as pd                             # Преобразовать Словари в Таблицы
import sqlite3 as sq                            # Библиотека  Работа с БД
from data_bases.path_to_base import DATABASE        # Путь к БД

# responce = requests.post(url, auth, data, headers=headers) # Возможно необходимо прописать Заголовок headers = {'user-agent': 'my-app/0.0.1'}

import requests                                 # Библиотека для создания и обработки запросов

# Допустимый Формат Написания Торговых Пар (Символов)
# symbol='del_usdt' - родной
# symbol='DEL/USDT' - Унификация с ccxt. Преобразуется в del_usdt



class BitTeam(): # Request
    base_url = 'https://bit.team/trade/api'
    status = None # Статус-код последнего запроса 200 - если ок
    data = None # Данные последнего запроса
    database = DATABASE
    auth = None

    def __init__(self, account={'apiKey': None, 'secret': None}):
        self.account = account

    @staticmethod
    def format_symbol(symbol: str): # Привожу Унифицированный Формат к Родному
        return symbol.lower().replace('/', '_')

    def fetch_order_book(self, symbol='del_usdt'): #
        """
        Стакан Цен по выбранной Паре
        Также Стакан есть и в запросе "pair". Но там он обрезан лимитом в 50 слотов
        """
        symbol = self.format_symbol(symbol)
        end_point = f'{self.base_url}/orderbooks/{symbol}'
        responce = requests.get(url=end_point)
        self.status = responce.status_code
        self.data = responce.json()
        return self.data

    def fetch_tiker(self, symbol='del_usdt'):
        """
        Весь Стакан есть и в запросе "orderbooks". Здесь он обрезан лимитом в 50 слотов
        # Мин. шаг размера Лота. Кол-во знаков в Дроби после целой части. int()
        print(f"Шаг Размера Лота: {self.date['result']['pair']['baseStep']}")
        # Кол-во знаков в Дроби после целой части. str()
        print(f"ЦЕНА. Кол-во Знаков после целой части: {self.date['result']['pair']['settings']['price_view_min']}")
        # Кол-во знаков в Дроби после целой части. str()
        print(f"Размер Позы. Кол-во Знаков после целой части: {self.date['result']['pair']['settings']['lot_size_view_min']}")
        # Мин. размер Лота относительно Доллара US. str()
        print(f"Мин. Размер Позы в USD: {self.date['result']['pair']['settings']['limit_usd']}")
        """
        symbol = self.format_symbol(symbol)
        end_point = f'{self.base_url}/pair/{symbol}'
        responce = requests.get(url=end_point)
        self.status = responce.status_code
        self.data = responce.json()
        return self.data

    def info_symbols(self):
        """
        Метод для получения информации обо всех торговых парах
        """
        end_point = f'{self.base_url}/pairs'
        # dt_now = self.get_moment_date()
        responce = requests.get(url=end_point)
        self.status = responce.status_code
        self.data = responce.json()
        return self.data

    def load_symbols_database(self): # Применять ТОЛЬКО сразу после Метода info_symbols
        """
        Получает данные по Всем парам и записывает их в базу Данных SQL.
        id, name, baseStep, quoteStep
        Перед записью существующие записи удаляет.
        """
        self.info_symbols()

        with sq.connect(self.database) as connect:
            # connect_db.row_factory = sq.Row  # Если хотим строки записей в виде dict {}. По умолчанию - кортежи turple ()
            curs = connect.cursor()
            curs.execute("""CREATE TABLE IF NOT EXISTS Symbols
                (id INTEGER PRIMARY KEY, name TEXT, baseStep INTEGER, quoteStep INTEGER)""")
            curs.execute("""DELETE FROM Symbols""")
            for symbol in self.data['result']['pairs']:
                curs.execute("""
            INSERT INTO Symbols (id, name, baseStep, quoteStep) 
            VALUES (:Id, :Name, :BaseStep, :QuoteStep)
             """, {'Id': symbol['id'], 'Name': symbol['name'], 'BaseStep': symbol['baseStep'], 'QuoteStep': symbol['quoteStep']})


# --- ПРИВАТНЫЕ ЗАПРОСЫ. Требуется Предварительная Авторизация -----------------------------



    def authorization(self):
        if (not self.account['apiKey']) or (not self.account['secret']):
            print('Ошибка Авторизации. Задайте/Проверьте Публичный и Секретный АПИ Ключи')
            # raise AuthorizationException
        basic_auth = requests.auth.HTTPBasicAuth(self.account['apiKey'], self.account['secret'])
        self.auth = basic_auth

    def fetch_balance(self):
        """
        Полный Баланс По Спот Аккаунту
        """
        if not self.auth: self.authorization()
        end_point = f'{self.base_url}/ccxt/balance'
        responce = requests.get(url=end_point, auth=self.auth)
        self.status = responce.status_code
        self.data = responce.json()
        return self.data['result']

    def create_order_original(self, body: dict):
        """
        body = {'pairId':   str, #  '24' del_usdt
                'side':     str, # "buy", "sell"
                'type':     str, # "limit", "market"
                'amount':   str, # '330' (value in coin1 (farms))
                'price':    str  # '0.04' (price in base coin (usdt))
                }
        """
        end_point = f'{self.base_url}/ccxt/ordercreate'
        responce = requests.post(url=end_point, auth=self.auth, data=body)
        self.status = responce.status_code
        self.data = responce.json()
        if self.status == 200:
            print(f'BitTeam. Создан Ордер ID: {self.data["result"]["id"]}')
        else:
            print(f'BitTeam_DONT_create_order_{body["pairId"]}_{body["side"]}_{body["type"]}_{body["amount"]}_{body["price"]}')
            print(self.data)
        return self.data # Доработать ВЕРНУТЬ инфу для заполнения таблицы Ордеров в Базе Данных!

    def get_pairId_database(self, symbol):
        with sq.connect(self.database) as connect:
            curs = connect.cursor()
            curs.execute("""SELECT id FROM Symbols WHERE name LIKE ?""", [symbol])
            return str(curs.fetchone()[0])

    def create_order(self, symbol: str, type: str, side: str, amount: float, price: float):
        """
        Привести к Виду:
        body = {'pairId':   str, #  '24' del_usdt
                'side':     str, # "buy", "sell"
                'type':     str, # "limit", "market"
                'amount':   str, # '330' (value in coin1 (farms))
                'price':    str  # '0.04' (price in base coin (usdt))
                }
        """
        symbol = self.format_symbol(symbol)
        pairId = self.get_pairId_database(symbol)
        body = {'pairId': pairId,
                'side': side,
                'type': type,
                'amount': str(round(amount, 6)), # пока округляю до 6 знаков
                'price': str(round(price, 6))   # пока округляю до 6 знаков
                }
        end_point = f'{self.base_url}/ccxt/ordercreate'
        responce = requests.post(url=end_point, auth=self.auth, data=body)
        self.status = responce.status_code
        self.data = responce.json()
        if self.status == 200:
            print(f'BitTeam. Создан Ордер ID: {self.data["result"]["id"]}')
        else:
            print(f'BitTeam_DONT_create_order_{body["pairId"]}_{body["side"]}_{body["type"]}_{body["amount"]}_{body["price"]}')
            print(self.data)
        return self.data # Доработать ВЕРНУТЬ инфу для заполнения таблицы Ордеров в Базе Данных!


# class AuthorizationException(Exception):
#     print('Ошибка Авторизации. Задайте/Проверьте Публичный и Секретный АПИ Ключи')
