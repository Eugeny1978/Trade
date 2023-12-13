from connectors.bitteam import BitTeam
import ccxt


class AnyExchange:
    def __init__(self, exchange_name):
        self.name_exchange = exchange_name

def connect_to_bitteam():
    print('Соединение с BitTeam')
    return BitTeam()

def connect_to_binance():
    print('Соединение с Binance')
    return ccxt.binance()

def connect_to_bybit():
    print('Соединение с ByBit')
    return ccxt.bybit()


connect_to_exchange = {
            'BitTeam': connect_to_bitteam,
            'Binance': connect_to_binance,
            'ByBit': connect_to_bybit
        }

def main():
    ex = AnyExchange('BitTeam')
    exchange = connect_to_exchange[ex.name_exchange]()
    orderbook = exchange.fetch_order_book()
    print(orderbook)

main()




