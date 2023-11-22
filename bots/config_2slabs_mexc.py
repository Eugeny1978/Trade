ACCOUNT = 'Luchnik_Mexc' # Имя Аккаунта в Базе Данных

SYMBOL = 'MX/USDT'     # Торгуемая Пара
VOLUME_BASE = 28     # Количество исользуемых Средств Базовой Валюты (в абс. значениях)
VOLUME_QUOTE = 80  # Количество исользуемых Средств Базовой Валюты (в абс. значениях)
PART_carrot = 25    # Часть (в %) от общих Используемых Средств для Приманок
PART_1slab = 40     # Часть (в %) от общих Используемых Средств для 1-го Уровня Плит
PART_2slab = 35     # Часть (в %) от общих Используемых Средств для 2-го Уровня Плит
LEVEL_1slab = 8.0   # Уровень Цен для 1-го Уровня Плит. = Стартовая Цена +- Х % от этой Цены
LEVEL_2slab = 10.0  # Уровень Цен для 2-го Уровня Плит. = Стартовая Цена +- Х % от этой Цены
MIN_SPRED = 4.0     # расстояние между Стартовой ценой и ближайшим Ордером-Приманкой (в процентах от Стартовой Цены)
SLEEP_Level = 6         # Частота корректировки Ордеров в сек
NUM_carrots = 3     # Кол-во Ордеров Приманок на каждый тип (buy, sell). Устанавливать в зависимости от используемых ср-в
MIN_AMOUNT = 10     # Минимальный Размер Ордера в USDT

# НЕ Настраиваемые Параметры. Устанавливаю статус Работы Бота ---------------------------
import sqlite3 as sq            # Работа с БД
from data_bases.path_to_base import DATABASE
bot_name = 'bot_2slabs_mexc'
# 'Run' - Запущен / 'Pause' (Теущие Ордера Стоят, Новые не ставятся) / 'Stop' - Остановлен. Ордера Удалены
BOT = 'Stop'

def set_bot_status_sql():
    with sq.connect(DATABASE) as connect:
        curs = connect.cursor()
        curs.execute(f"UPDATE BotStatuses SET status = '{BOT}' WHERE bot LIKE '{bot_name}'")

def main():
    set_bot_status_sql()

main()
