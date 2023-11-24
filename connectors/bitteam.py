import requests                                 # Библиотека для создания и обработки запросов
import sqlite3 as sq                            # Библиотека  Работа с БД
from typing import Literal                      # Создание Классов Перечислений
# import pandas as pd                           # Преобразовать Словари в Таблицы
from data_bases.path_to_base import DATABASE    # Путь к БД

# responce = requests.post(url, auth, data, headers=headers) # Возможно необходимо прописать Заголовок headers = {'user-agent': 'my-app/0.0.1'}
# Допустимый Формат Написания Торговых Пар (Символов)
# symbol='del_usdt' - родной
# symbol='DEL/USDT' - Унификация с ccxt. Преобразуется в del_usdt

OrderSide = Literal['buy', 'sell']
OrderType = Literal['limit', 'market']
UserOrderTypes = Literal['history', 'active', 'closed', 'cancelled', 'all'] # history = closed + cancelled

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

    def fetch_ticker(self, symbol='del_usdt'):
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
        self.__load_symbols_database() # Возможно сделать доп проверку чтобы не постоянно скидывать в базу
        return self.data

    def __load_symbols_database(self): # Применять ТОЛЬКО сразу после Метода info_symbols
        """
        Получает данные по Всем парам и записывает их в базу Данных SQL.
        id, name, baseStep, quoteStep
        Перед записью существующие записи удаляет.
        """
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

    def __get_pairId_database(self, symbol):
        with sq.connect(self.database) as connect:
            curs = connect.cursor()
            curs.execute(f"SELECT id FROM Symbols WHERE name LIKE '{symbol}'")
            return str(curs.fetchone()[0])

    def create_order(self, symbol: str, type: OrderType, side: OrderSide, amount: float, price: float):
        """
        Привести к Виду:
        body = {'pairId':   str, #  '24' del_usdt
                'side':     str, # "buy", "sell"
                'type':     str, # "limit", "market"
                'amount':   str, # '330' (value in coin1 (farms))
                'price':    str  # '0.04' (price in base coin (usdt))
                }
        """
        if not self.auth: self.authorization()
        pairId = self.__get_pairId_database(self.format_symbol(symbol))
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
        # if self.status == 200:
        #     print(f'BitTeam. Создан Ордер ID: {self.data["result"]["id"]}')
        # else:
        #     print(f'BitTeam_DONT_create_order_{symbol}_{side}_{type}_{body["amount"]}_{body["price"]}')
        #     print(self.data)
        return self.data # Доработать ВЕРНУТЬ инфу для заполнения таблицы Ордеров в Базе Данных!

    def cancel_order(self, id: (int, str)):
        """
        cancel_order(self, id: str, symbol: Optional[str] = None, params={}) # ccxt
        id_order = data['result']['id'] # create_order(body)
        """
        if not self.auth: self.authorization()
        end_point = f'{self.base_url}/ccxt/cancelorder'
        body = {"id": id}
        responce = requests.post(url=end_point, auth=self.auth, data=body)
        self.status = responce.status_code
        self.data = responce.json()
        # if self.status == 200:
        #     print(f'BitTeam. Удален Ордер ID: {id}')
        # else:
        #     print(f'BitTeam. Ордер ID: {id} - НЕ Удален')
        return self.data # Подумай что он должен вернуть

    def cancel_all_orders(self, symbol=None):
        """
        cancel_all_orders(self, symbol: Optional[str] = None, params={}) # ccxt
        pairId 1-100 - по конкретной паре || 0 - all pairs | 24 - del_usdt
        """
        if not self.auth: self.authorization()
        if symbol:
            pairId = self.__get_pairId_database(self.format_symbol(symbol))
        else:
            pairId = 0
        end_point = f'{self.base_url}/ccxt/cancel-all-order'
        body = {"pairId": pairId}
        responce = requests.post(url=end_point, auth=self.auth, data=body)
        self.status = responce.status_code
        self.data = responce.json()
        if self.status == 200 and not pairId:
            print(f'BitTeam. Удалены ВСЕ Ордера')
        elif self.status == 200:
            print(f'BitTeam. Удалены Все Ордера по Символу: {symbol}')
        else:
            print(f'BitTeam. Ордера НЕ Удалены. | Символ: {symbol}')
        return self.data # Подумай что он должен вернуть

    def fetch_order(self, order_id: (int or str)):
        """
        # fetch_order(self, id: str, symbol: Optional[str] = None, params={})  # ccxt
        Информация об Ордере по его ID
        """
        if not self.auth: self.authorization()
        end_point = f'{self.base_url}/ccxt/order/{order_id}'
        responce = requests.get(url=end_point, auth=self.auth)
        self.status = responce.status_code
        self.data = responce.json()
        return self.data

    def fetch_orders(self, symbol=None, since=None, limit=1000, type:UserOrderTypes='active', offset=0, order='', where=''):
        """
        fetch_orders(self, symbol: Optional[str] = None, since: Optional[int] = None, limit: Optional[int] = None, params={})

        Ордера за Текущую Дату
        type= 'history', 'active', 'closed', 'cancelled', 'all'| history = closed + cancelled
        offset=х - смещение: не покажет первые Х ордеров
        {{baseUrl}}/trade/api/ccxt/ordersOfUser?limit=10&offset=0&type=active&order=<string>&where=<string>
        """
        # Необязательные Параметры
        url_limit = '' if limit == 10 else f'&limit={limit}'
        url_offset = '' if offset == 0 else f'&offset={offset}'
        url_order = '' if order == '' else f'&order={order}'
        url_where = '' if where == '' else f'&where={where}'
        if not self.auth: self.authorization()
        end_point = f'{self.base_url}/ccxt/ordersOfUser?type={type}' + url_limit + url_offset + url_order + url_where
        responce = requests.get(url=end_point, auth=self.auth)
        self.status = responce.status_code
        self.data = responce.json()
        if self.status == 200 and symbol:
            self.__filter_orders(self.format_symbol(symbol))
        return self.data

    def __filter_orders(self, symbol):
        count = 0
        data_orders = []
        for order in self.data['result']['orders']:
            if order['pair'] == symbol:
                data_orders.append(order)
                count += 1
        self.data['result']['orders'] = data_orders
        self.data['result']['count'] = count

    def fetch_my_trades(self, symbol=0, limit=10, offset=0, order=''):
        """
        Сделки за Последние 3 дня ? (тесты показали что вроде так - устанавливал лимит 100)
        offset=х - смещение: не покажет первые Х сделок
        pairId=0 - все пары # 24 - del_usdt
        ccxt/tradesOfUser?limit=10&offset=0&order=<string>&pairId=<integer>
        созданный мной в RequestAPI:
        get_trades_of_user(self, limit=10, offset=0, order='', pairId=0):
        ccxt:
        fetch_my_trades(self, symbol: Optional[str] = None, since: Optional[int] = None, limit: Optional[int] = None, params={}):
        """
        # Необязательные Параметры
        url_limit = '' if limit == 10 else f'limit={limit}'
        url_offset = '' if not offset else f'&offset={offset}'
        url_order = '' if not order else f'&order={order}'
        if not symbol: url_pairId = ''
        else:
            pairId = self.__get_pairId_database(self.format_symbol(symbol))
            url_pairId = f'&pairId={pairId}'
        if not self.auth: self.authorization()
        end_point = f'{self.base_url}/ccxt/tradesOfUser?' + url_limit + url_offset + url_order + url_pairId
        responce = requests.get(url=end_point, auth=self.auth)

        self.status = responce.status_code
        self.data = responce.json()
        return self.data



# class AuthorizationException(Exception):
#     print('Ошибка Авторизации. Задайте/Проверьте Публичный и Секретный АПИ Ключи')
