
ACCOUNT = 'Luchnik_Binance_Test_Spot'
SYMBOL = 'ETH/USDT'               # Торгуемая Пара
VOLUME_BASE = 0.6
VOLUME_QUOTE = 1200
PART_carrot = 10 # %
PART_1slab = 50  # %
PART_2slab = 40  # %
LEVEL_1slab = 3 # %
LEVEL_2slab = 5 # %
MIN_SPRED = 0.5 # расстояние между стартовой ценой и ближайшим Ордером (в процентах)
SLEEP_1slab = 60 # Частота корректировки Ордеров в сек
SLEEP_2slab = 555 # Частота корректировки Ордеров в сек
NUM_carrots = 10 # количество Ордеров приманок на каждый тип (buy sell)

# НЕ Настраиваемые Параметры ---------------------------
# STEP_PRICE = 6    # ШАГ Цен. Округлять до Знаков после точки
# STEP_AMOUNT = 6   # ШАГ Объемов. Округлять до Знаков после точки
MIN_AMOUNT = 10