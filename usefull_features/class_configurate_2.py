from connectors.bitteam import BitTeam
import ccxt


class AnyExchange:

    def connect_to_bitteam(self):
        print('Соединение с BitTeam')
        return BitTeam()

    def connect_to_binance(self):
        print('Соединение с Binance')
        return ccxt.binance()

    def connect_to_bybit(self):
        print('Соединение с ByBit')
        return ccxt.bybit()

    connect_to_exchange = {
                'BitTeam': connect_to_bitteam,
                'Binance': connect_to_binance,
                'ByBit': connect_to_bybit
            }

    def __init__(self, exchange_name):
        self.name_exchange = exchange_name
        self.connect = self.connect_to_exchange[exchange_name](self)
def main():
    ex = AnyExchange('BitTeam')
    print(ex.connect.fetch_order_book())


main()




