ACCOUNT = 'Luchnik_Bitteam' # Имя Аккаунта в Базе Данных
SYMBOL = 'DEL/USDT' # Торгуемая Пара
VOLUME_BASE = 1400   # Количество исользуемых Средств Базовой Валюты (в абс. значениях)
VOLUME_QUOTE = 23   # Количество исользуемых Средств Базовой Валюты (в абс. значениях)
PART_carrot = 10    # Часть (в %) от общих Используемых Средств для Приманок
PART_1slab = 50     # Часть (в %) от общих Используемых Средств для 1-го Уровня Плит
PART_2slab = 40     # Часть (в %) от общих Используемых Средств для 2-го Уровня Плит
LEVEL_1slab = 8     # Уровень Цен для 1-го Уровня Плит. = Стартовая Цена +- Х % от этой Цены
LEVEL_2slab = 10    # Уровень Цен для 2-го Уровня Плит. = Стартовая Цена +- Х % от этой Цены
MIN_SPRED = 5.0     # расстояние между Стартовой ценой и ближайшим Ордером-Приманкой (в процентах от Стартовой Цены)
SLEEP_1slab = 5    # Частота корректировки Ордеров в сек
SLEEP_2slab = 5   # Частота корректировки Ордеров в сек
NUM_carrots = 10    # Кол-во Ордеров Приманок на каждый тип (buy, sell). Устанавливать в зависимости от используемых ср-в

# НЕ Настраиваемые Параметры ---------------------------
MIN_AMOUNT = 10 # Минимальный Размер Ордера в USDT
