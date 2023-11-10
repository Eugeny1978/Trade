import requests                                 # Библиотека для создания и обработки запросов
# from api.request import Request                 # Базовый Класс
import pandas as pd                             # Преобразовать Словари в Таблицы
import sqlite3 as sq                            # Библиотека  Работа с БД
from data_bases.path_to_base import DATABASE        # Путь к БД

# responce = requests.post(url, auth, data, headers=headers) # Возможно необходимо прописать Заголовок headers = {'user-agent': 'my-app/0.0.1'}

BASE_URL = 'https://bit.team/trade/api'
# account = {'name': 'Luchnik78', 'public_key': API, 'secret_key': PRIVATE}
ACCOUNT = {'name': 'Luchnik78', 'exchange': 'Bitteam'}

class RequestBitTeam(): # Request


# --- ПУБЛИЧНЫЕ ЗАПРОСЫ. НЕ Требуется Предварительная Авторизация -----------------------------

    def get_orderbooks(self, pair='del_usdt'):
        """
        Стакан Цен по выбранной Паре
        Также Стакан есть и в запросе "pair". Но там он обрезан лимитом в 50 слотов
        """
        end_point = f'{BASE_URL}/orderbooks/{pair}'

        dt_now = self.get_moment_date()
        responce = requests.get(url=end_point)

        self.status = responce.status_code
        self.data = responce.json()
        self.file_name = f'BitTeam_orderbooks_{pair}_{dt_now}'

    def get_pair(self, pair='del_usdt'):
        """
        Весь Стакан есть и в запросе "orderbooks". Здесь он обрезан лимитом в 50 слотов
        """
        end_point = f'{BASE_URL}/pair/{pair}'

        dt_now = self.get_moment_date()
        responce = requests.get(url=end_point)

        self.status = responce.status_code
        self.data = responce.json()
        self.file_name = f'BitTeam_pair_{pair}_{dt_now}'

        # # Мин. шаг размера Лота. Кол-во знаков в Дроби после целой части. int()
        # print(f"Шаг Размера Лота: {self.date['result']['pair']['baseStep']}")
        # # Кол-во знаков в Дроби после целой части. str()
        # print(f"ЦЕНА. Кол-во Знаков после целой части: {self.date['result']['pair']['settings']['price_view_min']}")
        # # Кол-во знаков в Дроби после целой части. str()
        # print(f"Размер Позы. Кол-во Знаков после целой части: {self.date['result']['pair']['settings']['lot_size_view_min']}")
        # # Мин. размер Лота относительно Доллара US. str()
        # print(f"Мин. Размер Позы в USD: {self.date['result']['pair']['settings']['limit_usd']}")

    def info_pairs(self):
        """
        Метод для получения информации обо всех торговых парах
        """
        end_point = f'{BASE_URL}/pairs'

        dt_now = self.get_moment_date()
        responce = requests.get(url=end_point)

        self.status = responce.status_code
        self.data = responce.json()
        self.file_name = f'BitTeam_all_pairs_{dt_now}'

    def post_pairs_sql(self):
        """
        Получает данные по Всем парам и записывает их в базу Данных SQL.
        id, name, baseStep, quoteStep
        Перед записью существующие записи удаляет.
        """
        self.info_pairs()

        with sq.connect(DATABASE) as connect:
            # connect_db.row_factory = sq.Row  # Если хотим строки записей в виде dict {}. По умолчанию - кортежи turple ()
            curs = connect.cursor()

            curs.execute("""CREATE TABLE IF NOT EXISTS pairs
                (id INTEGER PRIMARY KEY, name TEXT, baseStep INTEGER, quoteStep INTEGER)""")

            curs.execute("""DELETE FROM pairs""")

            for pair in self.data['result']['pairs']:
                curs.execute("""
                    INSERT INTO pairs (id, name, baseStep, quoteStep) 
                    VALUES (:Id, :Name, :BaseStep, :QuoteStep)
                     """, {'Id': pair['id'], 'Name': pair['name'], 'BaseStep': pair['baseStep'],
                           'QuoteStep': pair['quoteStep']})



# --- ПРИВАТНЫЕ ЗАПРОСЫ. Требуется Предварительная Авторизация -----------------------------


    def get_api_keys(self, account: dict):
        with sq.connect(DATABASE) as connect_db:
            connect_db.row_factory = sq.Row  # Если хотим строки записей в виде dict {}. По умолчанию - кортежи turple ()
            cursor_db = connect_db.cursor()
            cursor_db.execute("""SELECT name, public_key, secret_key FROM trade_api
                              WHERE name LIKE :Name and exchange LIKE :Exchange
                              """, {'Name': account['name'], 'Exchange': account['exchange']})
            for select in cursor_db:
                self.account_name = select['name']
                self.public_key = select['public_key']
                self.secret_key = select['secret_key']

    def authorization(self, account):
        self.get_api_keys(account)
        basic_auth = requests.auth.HTTPBasicAuth(self.public_key, self.secret_key)
        self.auth = basic_auth

    def get_balance(self):
        """
        Полный Баланс По Спот Аккаунту
        """
        end_point = f'{BASE_URL}/ccxt/balance'

        dt_now = self.get_moment_date()
        responce = requests.get(url=end_point, auth=self.auth)

        self.status = responce.status_code
        self.data = responce.json()
        self.file_name = f'BitTeam_balance_{self.account_name}_{dt_now}'

    def get_balance_compact(self) -> pd.DataFrame:
        """
        Компактный Баланс По Спот Аккаунту в виде DataFrame
        """

        self.get_balance()
        data = self.data['result']
        types = ('free', 'used', 'total')

        df = pd.DataFrame(columns=types)
        for key_coin in data.keys():
            if key_coin not in types:
                for key_type in data[key_coin].keys():
                    if data[key_coin][key_type] != '0':
                        df.loc[key_coin] = data[key_coin][types[0]], data[key_coin][types[1]], data[key_coin][types[2]]
                        # df.loc[key_coin] = float(data[key_coin][types[0]]), float(data[key_coin][types[1]]), float(data[key_coin][types[2]])
                        break
        print(df)
        self.balance = df

        # Результат В виде Словаря
        # data_not_zero = {}
        # for key in data.keys():
        #     if key in selection:
        #         data_not_zero[key] = {}
        #         for k_coin in data[key].keys():
        #             if data[key][k_coin] != '0':
        #                 data_not_zero[key][k_coin] = data[key][k_coin]

    def create_order(self, body: dict):
        """
        body = {'pairId':   str, #  '44' farms_usdt, '24' del_usdt
                'side':     str, # "buy", "sell"
                'type':     str, # "limit", "market", ??? - "conditional" - отрабатывает, и глючит, но цена прикоторой ордер превhатится в лимитный Космическая
                'amount':   str, # '330' (value in coin1 (farms))
                'price':    str  # '0.04' (price in base coin (usdt))
                }
        """
        end_point = f'{BASE_URL}/ccxt/ordercreate'
        responce = requests.post(url=end_point, auth=self.auth, data=body)

        self.status = responce.status_code
        self.data = responce.json()
        if self.status == 200:
            file_name = f'BitTeam_create_order_{self.data["result"]["pair"]}_{body["side"]}_{body["type"]}_{body["amount"]}_{body["price"]}_{self.data["result"]["id"]}'
            print(f'BitTeam. Создан Ордер ID: {self.data["result"]["id"]}')
        else:
            file_name = f'BitTeam_DONT_create_order_{body["pairId"]}_{body["side"]}_{body["type"]}_{body["amount"]}_{body["price"]}'
            print(self.data)
        self.file_name = file_name


    def get_order(self, order_id: int):
        """
        Информация об Ордере по его ID
        """
        end_point = f'{BASE_URL}/ccxt/order/{order_id}'
        responce = requests.get(url=end_point, auth=self.auth)

        self.status = responce.status_code
        self.data = responce.json()
        self.file_name = f'BitTeam_get_order_{order_id}'


    def cancel_order(self, order_id: str):
        """
        id_order = data['result']['id'] # create_order(body)
        """
        end_point = f'{BASE_URL}/ccxt/cancelorder'
        body = {"id": order_id}
        responce = requests.post(url=end_point, auth=self.auth, data=body)

        self.status = responce.status_code
        self.data = responce.json()
        if self.status == 200:
            file_name = f'BitTeam_cancel_order_{order_id}'
            print(f'BitTeam. Удален Ордер ID: {order_id}')
        else:
            file_name = f'BitTeam_DONT_cancel_order_{order_id}'
        self.file_name = file_name


    def cancel_all_orders(self, pairId=0):
        """
        pairId 1-100 - по конкретной паре || 0 - all pairs | 24 - del_usdt
        """
        end_point = f'{BASE_URL}/ccxt/cancel-all-order'
        body = {"pairId": pairId}
        responce = requests.post(url=end_point, auth=self.auth, data=body)

        self.status = responce.status_code
        self.data = responce.json()
        if self.status == 200 and not pairId:
            file_name = f'BitTeam_cancel_ALL_orders'
            print(f'BitTeam. Удалены ВСЕ Ордера')
        elif self.status == 200:
            file_name = f'BitTeam_cancel_all_orders_{pairId}'
            print(f'BitTeam. Удалены Все Ордера по Паре (PairId): {pairId}')
        else:
            file_name = f'BitTeam_DONT_cancel_all_orders_{pairId}'
        self.file_name = file_name


    def get_orders_of_user(self, type='active', limit=10, offset=0, order='', where=''):
        """
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

        end_point = f'{BASE_URL}/ccxt/ordersOfUser?type={type}' + url_limit + url_offset + url_order + url_where

        dt_now = self.get_moment_date()
        responce = requests.get(url=end_point, auth=self.auth)

        self.status = responce.status_code
        self.data = responce.json()
        self.file_name = f'BitTeam_orders_of_user_{type}_{dt_now}'

    def get_trades_of_user(self, limit=10, offset=0, order='', pairId=0):
        """
        Сделки за Последние 3 дня ? (тесты показали что вроде так - устанавливал лимит 100)
        offset=х - смещение: не покажет первые Х сделок
        pairId=0 - все пары # 24 - del_usdt
        ccxt/tradesOfUser?limit=10&offset=0&order=<string>&pairId=<integer>
        """
        # Необязательные Параметры
        url_limit = '' if limit == 10 else f'limit={limit}'
        url_offset = '' if offset == 0 else f'&offset={offset}'
        url_order = '' if order == '' else f'&order={order}'
        url_pairId = '' if pairId == 0 else f'&pairId={pairId}'

        dt_now = self.get_moment_date()
        end_point = f'{BASE_URL}/ccxt/tradesOfUser?' + url_limit + url_offset + url_order + url_pairId
        responce = requests.get(url=end_point, auth=self.auth)

        self.status = responce.status_code
        self.data = responce.json()
        self.file_name = f'BitTeam_trades_of_user_{dt_now}'


# ---- # Конструкция для выполнения кода из этого файла -----------------------------------------
def main():

    req = RequestBitTeam()

    # Публичные Запросы ------------------------------------------

    # req.get_orderbooks()   # Получение Стакана Цен

    # req.get_pair()         # Информация по Торгуемой Паре

    # req.info_pairs() # Информация по Всем Торгуемым Парам
    # req.post_pairs_sql() # Отправить Информацию по Всем Торгуемым Парам в БД

    # Приватные Запросы -----------------------------------------
    req.authorization(ACCOUNT)
    # req.get_balance_compact()

    # # req.get_balance()

    # body_order = {'pairId': '24',  # del_usdt
    #               'side': "sell",
    #               'type': "limit",
    #               'amount': '6.123456',  # '6.12345678' 8 знаков после точки
    #               'price': '0.018991'} # '0.017991' 6 знаков после точки
    # req.create_order(body_order)

    # req.get_order(101922459)

    # req.cancel_order('101922459')

    req.cancel_all_orders('24')

    # req.get_orders_of_user()
    # order_types = ('history', 'active', 'closed', 'cancelled', 'all')
    # for ot in order_types:
    #     req.get_orders_of_user(type=ot)
    #     req.write_data()

    # req.get_trades_of_user(limit=100)

# Контроль Результатов -------------------------------------------------

    # print(req.__dict__)  # Вывод на экран Атрибутов Экземляра Класса
    req.write_data()  # Запись Данных в файл


if __name__ == '__main__':
    main()