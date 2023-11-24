ACCOUNT = 'Luchnik_Bitteam' # 'Constantin_BitTeam'  #  # Имя Аккаунта в Базе Данных

SYMBOL = 'DEL/USDT'     # Торгуемая Пара
VOLUME_BASE = 2900      # Количество исользуемых Средств Базовой Валюты (в абс. значениях)
VOLUME_QUOTE = 50       # Количество исользуемых Средств Базовой Валюты (в абс. значениях)


# НЕ Настраиваемые Параметры. Устанавливаю статус Работы Бота ---------------------------
import sqlite3 as sq            # Работа с БД
from data_bases.path_to_base import DATABASE
bot_name = 'bot_2slabs_bitteam'
# 'Run' - Запущен / 'Pause' (Теущие Ордера Стоят, Новые не ставятся) / 'Stop' - Остановлен. Ордера Удалены
BOT = 'Stop'

def set_bot_status_sql():
    with sq.connect(DATABASE) as connect:
        curs = connect.cursor()
        curs.execute(f"UPDATE BotStatuses SET status = '{BOT}' WHERE bot LIKE '{bot_name}'")

def main():
    set_bot_status_sql()

main()