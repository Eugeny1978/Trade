import ccxt
import pandas as pd

pd.options.display.width= None # Отображение Таблицы на весь Экран
pd.options.display.max_columns= 20 # Макс Кол-во Отображаемых Колонок
pd.options.display.max_rows= 20 # Макс Кол-во Отображаемых Колонок
div_line = '-------------------------------------------------------------------------------------'

MIN_USDT = 500

exchanges = {
    'Binance': ccxt.binance,
    'BitTeam': ccxt.bitteam,
    'ByBit': ccxt.bybit,
    'GateIo': ccxt.gateio,
    'Mexc': ccxt.mexc,
    'Okx': ccxt.okx
}

def get_balance(exchange):
    try:
        balance = exchange.fetch_balance()
        indexes = ['free', 'used', 'total']
        columns = [balance['free'], balance['used'], balance['total']]
        df = pd.DataFrame(columns, index=indexes)
        df_compact = df.loc[:, (df != 0).any(axis=0)]  # убирает Столбцы с 0 значениями
    except Exception as error:
        df_compact = None
        print(error)
    return df_compact

def get_rate(balance: pd.DataFrame):
    try:
        usdt = balance['USDT']['total']
        rate = round(usdt/MIN_USDT, 1)
        if rate < 1: rate = 1
    except:
        rate = 0
    return rate

def print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password=''):
    keys =  {'apiKey': acc_apikey, 'secret': acc_secret, 'acc_password': acc_password}
    exchange = exchanges[exchange_name](keys)
    balance = get_balance(exchange)
    rate = get_rate(balance)
    print(account_name, exchange_name, balance, f"Rate = {rate}", div_line, sep='\n')
    return exchange


if __name__ == '__main__':

    # account_name = 'Koziakova Janna_ByBit' # 'Кошмелев Сергей'
    # exchange_name = 'ByBit'
    # acc_apikey = 'dlvnWflJSmeCUdMKiS'
    # acc_secret = '7ri4UMUkvmj9KYu8pbIHRz2T0cJWoxvz3F6e'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Koziakova Janna_Mexc'  # 'Кошмелев Сергей'
    # exchange_name = 'Mexc'
    # acc_apikey = 'mx0vglQ9OdqKjW8n1q'
    # acc_secret = 'c8903b90fc7042179b115a8be3a4ad1a'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Koshmelev_Sergey_ByBit' # 'Кошмелев Сергей'
    # exchange_name = 'ByBit'
    # acc_apikey = 'H5gg5XNhxe3Tz9q7ZZ'
    # acc_secret = 'IHKJMgJtrXVqJL68mmyhv1fvdLBRqKIpjAUs'
    # exchange = print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    # # exchange.create_market_order(symbol='BTC/USDT', side='buy', amount=(10/40000), price=40000) #
    # exchange.create_order(symbol='BTC/USDT', side='buy', type='limit', amount=(20/38000), price=38000)
    # print(get_balance(exchange))

    # account_name = 'Belous Denis_ByBit'
    # exchange_name = 'ByBit'
    # acc_apikey = 'U54nMfRvbX4yMRuilf'
    # acc_secret = '7OGPRid20Kq8n2I6Plr7ZJRbuns4b9Uf1sZA'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Alehin Roman_ByBit'
    # exchange_name = 'ByBit'
    # acc_apikey = 'WdhF4vNANDOthhSewQ'
    # acc_secret = 'DmB8f6vSFsqKyzvjL3RVoD2frYEm2bSSFvm0'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Alehin Roman_Mexc'
    # exchange_name = 'Mexc'
    # acc_apikey = 'mx0vgl5eUCp3r6IcZG'
    # acc_secret = '836bb8aab4864b7b968d15733e745935'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Kuklov Petr Alexandrovich_ByBit'
    # exchange_name = 'ByBit'
    # acc_apikey = 'pwN4LFjlpctMzLEpAc'
    # acc_secret = 'snnvMtlFbnj0XSuz2DltDeggHTUs3WX31y1S'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Yavorsky Alexandr Eduardovich_ByBit'
    # exchange_name = 'ByBit'
    # acc_apikey = 'lNC6EiCpU4k92ZXCZU'
    # acc_secret = 'jsowyffd2PF35FjD1od1H1scOZRHxceI7F2i'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Kapsamunova Natalia_ByBit'
    # exchange_name = 'ByBit'
    # acc_apikey = 'ZBmYeEX5HXQQQdllx5'
    # acc_secret = 'YIaLJfqs5Iha44wk5hSI8qadc5IQvws4p2bU'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Kapsamunova Natalia_ByBit'
    # exchange_name = 'Mexc'
    # acc_apikey = 'mx0vgl8SdJJUVmsg7V'
    # acc_secret = 'acaf63b9bb47408fa1422385f232d4af'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Zdanevich Alexandr Nikolaevich'
    # exchange_name = 'ByBit'
    # acc_apikey = 'r1zEmE3vfTkRR7UhA8'
    # acc_secret = '7YxNRzKrwoZxWHvrtmPvuUfRqYYKGdv6aw9r'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Shapovalov Anatoly Alexeevich'
    # exchange_name = 'ByBit'
    # acc_apikey = 'ESO954QeBWzw7I2BDp'
    # acc_secret = 'OdseKiVxKvoP5RuIHz2PXktgOkfOk0yUM2Hf'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Barnett Victoria'
    # exchange_name = 'ByBit'
    # acc_apikey = 'QWakUjM0tqi0dpRfEW'
    # acc_secret = 'ycBQJ6wsNcVNyN9cpsXYnaZNgmTeVtmdqqNr'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Mironov Vitaly Vladimirovich'
    # exchange_name = 'ByBit'
    # acc_apikey = 'ldmHgekNxySpRqnAZh'
    # acc_secret = 'yJ38Q0ywWp5eqvjTspZHO4yawtqoxUR8hDyq'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Garanin Andrey Pavlovich'
    # exchange_name = 'ByBit'
    # acc_apikey = 'yUx5jvGRzuM8rNG8QD'
    # acc_secret = 'B1T0DGGrUccViRPl9pyWdoVIapHMlw3fuh17'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Garanin Andrey Pavlovich'
    # exchange_name = 'Mexc'
    # acc_apikey = 'mx0vglRDd61RwAlqI3'
    # acc_secret = '691a0dfd63d44a78bc9c6544b2d048fd'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Dusmuhanbetov Eldar Kadrabaevich'
    # exchange_name = 'ByBit'
    # acc_apikey = 'or2RZqH2e1aTsSCQzG'
    # acc_secret = 'W4oKpL8EhtOArJ9NZxRB7JjFMYWkMm5XiBB0'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Dusmuhanbetov Eldar Kadrabaevich'
    # exchange_name = 'Mexc'
    # acc_apikey = 'mx0vglu0Xz6i5PhZRh'
    # acc_secret = 'b9611c6a6e8b4ac69e8f36b64d6ad57f'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Zinnatov Elmir Favadisovich'
    # exchange_name = 'ByBit'
    # acc_apikey = '1AJCwFSCK6wUMmIhEC'
    # acc_secret = 'CGJtL41y2aMvjfRX7GF6OvlG544uNKB6l3nv'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Zinnatov Elmir Favadisovich'
    # exchange_name = 'Mexc'
    # acc_apikey = 'mx0vglThXSID46qpC0'
    # acc_secret = '26672ac0a97741b0beea2cf38752ca73'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Bashkin Andrey Victorovich'
    # exchange_name = 'ByBit'
    # acc_apikey = '3ZzFYUUAD9rG5ebxMH'
    # acc_secret = 'IKkOziaXifc1JYukIxOkE1fdgyGWTgiGIGM3'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Evreev Timur'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'Dk7PgUZ3wOPmZzPAxx'
    # acc_secret = '8LU975xbmZZPhvWmsxeDb788208c3L2H767U'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Vlad'  # фамилия?
    # exchange_name = 'ByBit'
    # acc_apikey = 'hGNHqF9vO7ixvEJ1Wg'
    # acc_secret = 'yImWwbFYNUCQvLFlrCyD54N1zl6rvfXxEpbl'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Kubarev Mihail'  # новые ключи 2024.01.25 0 на счету
    # exchange_name = 'ByBit'
    # acc_apikey = 'EyavSYjfjn1gcTIbQJ'
    # acc_secret = 'ZmgCQJegXV6GY30CLwhmDY8cpW5FBv3xWLOQ'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Kokliaeva Marina Alexandrovna'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'xowpk5Vza66XBIkJIL'
    # acc_secret = 'zKwqJ5QuY01YzoqGFWMqMkSyt4XYezuo5cdV'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Klimov Yaroslav Evgenievich'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'MTe02bX9tfiZRbKHJz'
    # acc_secret = 'ivIWcDWj1WGXfn053zgh97cUaPneywi0OVAT'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Shmykov Viktor'  #
    # exchange_name = 'Binance'
    # acc_apikey = 'BFdEzF2pmTFO1qMLayHAzMqTegnzwajZ3qL70mxtQOnOeyn86HRpb3R4Erg5I42v'
    # acc_secret = '9kGZiQqHfeGXu42XGwk7aPsrf9sEOjGyOEloRLoSFKR0uv0bnLAul385Vzciqd7J'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Suslov Stanislav Gennagievich'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'A5T1cRDCiAkG8HZ5H1'
    # acc_secret = 'LOJuImrWftVZzhEscrQ0YyZnvIgQKVQTlkqb'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Latchenkov Sergey'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'bEApgln66CiNHIv2Om'
    # acc_secret = 'K516NAEFBYt75SDwAOKZAZYTONX3p42Vo7CC'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Gorsky Alexandr Vladimirovich'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'yV4N7OlecnUVH0tSGK'
    # acc_secret = 'bqpljjDDjieDGO9KEPqAs7Yz1rb0j67HFdcQ'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Ivanov Alexey Vladimirovich'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'kBy6LaYkIQDehTNT6G'
    # acc_secret = 'lIqMjIL2O11oXrELfT8gFcbse8bTYuAgOSA0'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Zvereva Olga Sergeevna'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'AdozuGJZSgO6LxOE6U'
    # acc_secret = 'v7arMnKsEQrKlVFScdaoxH3E60Zt7l96cyp8'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Nikulina Natalia'  # 400 долл. но торговать нельзя Проверить настройким АПИ галочки
    # exchange_name = 'ByBit'
    # acc_apikey = 'iG5ogE5Bh7UoaHRURs'
    # acc_secret = 'eYHs8ndsuroOD3d3u7Oc9tZItKN3B5keHE4B'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Nikulina Natalia'  #
    # exchange_name = 'Mexc'
    # acc_apikey = 'mx0vglBZrL9xwnM4Sc'
    # acc_secret = '52618073f63e4ed68cd75bfe5ffaf5e6'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Cherdanzev Maxim Nikolaevich'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'CyvrSR7zWq2mxzemjX'
    # acc_secret = 'pqdVomyTLd0qJMHb5rWS3IrlCuwQgsw57FMJ'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Korshunov Alexey'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'RHDO43lF8GogXTptSl'
    # acc_secret = 'NpRXmcMtSxHfJlLt8txViyRScAbhhuSsqRt8'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Stadnik Tatiana'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'dSYn4ePL1SwvUVMsSB'
    # acc_secret = 'ErbZYbeWphKP0wfODQM87LhIADK62NbfdO2C'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Donchenko Dmitry Vladimirovich'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'bf8lcaTGabVcYJNQim'
    # acc_secret = '5kXJnrTky2HM6ZfqPwwunDqWkGqlJ3BQbvgt'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Bikbova Rimma Rahmitovna'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'AZYpcSg5dMxdm5EJdm'
    # acc_secret = 'eRzBuasL1VOWF4wlkte0TH9UmIN5THOCU2RW'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Klays Daniel'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'GyDnd14pKH8nltaubA'
    # acc_secret = 'PP6HwXIbs5JMATCbf7TIIcLNkRW7KrCZkq3b'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Gorsky Alexandr Vladimirovich'  #
    # exchange_name = 'Mexc'
    # acc_apikey = 'mx0vgllGxqpwt4M56Q'
    # acc_secret = 'ac083686dd3548b5b176c897290c9fa7'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Sherer Olga Mihailovna'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'MRpL5tY1bsfMV5z5UB'
    # acc_secret = 'q84dbzGiBTWzj8jBpHA7piWLoD5rYh5DBUDQ'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Korshunov Alexey'  #
    # exchange_name = 'Mexc'
    # acc_apikey = 'mx0vglseYyL9sUqqhQ '
    # acc_secret = 'cd7e345a71ad49d581028457fa985f02'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Stadnik Tatiana'  #
    # exchange_name = 'BitTeam'
    # acc_apikey = '8ca88527ce306b16bb8628cb875179fc6d5c6d2759291686f05f1fa53eef'
    # acc_secret = 'cf89b676b0cb34df9dd3e6fa82a0a46e00ba690b9336c9cc98423687735ffdca8d9252e273844a5e'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Poselskaia Olga Alexandrovna'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'vAjsodeOqoXNwjEo88'
    # acc_secret = 'ydBFojz8fRdiVfVCR1ob9KfoyIozYVgqETcn'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Zvereva Olga Sergeevna'  # 0 средств. УДАЛИЛ ИЗ БАЗЫ
    # exchange_name = 'BitTeam'
    # acc_apikey = 'ed426ad5cff3c5642c87694250a6bed5732bc709c456466b39e6af98579f'
    # acc_secret = 'e00eb9c3448896df555ac694847d78a45c41ba726099af7b51bb6df64b39b1c609e364a77711f7e1'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Ivanov Alexey Vladimirovich'  #
    # exchange_name = 'BitTeam'
    # acc_apikey = '9f8712004a645afb615b28eb5391ad92ef6cd5d36b5551f721139771d9a3'
    # acc_secret = 'e692c8757402142414fe9a94b3995ebdebeed689e2dc40383073a471a5bf88b4e5af869ac9dda0c8'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Poselskaia Olga Alexandrovna'  # 254.99 USDT, 0.004099 BTC пока не подключаю
    # exchange_name = 'Mexc'
    # acc_apikey = 'mx0vglT3IQTptJMgm7'
    # acc_secret = 'd6b613f1723448bc920887e133bbf6ec'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Menshikov Grigory'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'mRwajWK4Ievinxi2Ce'
    # acc_secret = 'cFNwPnAtaexAPM5Aqcj0u5nR24NSOZHPeYFq'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Menshikov Grigory'  #
    # exchange_name = 'Mexc'
    # acc_apikey = 'mx0vgluF9kN3chLWmN'
    # acc_secret = 'e615be73a43b483583209a2e79930678'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Homiakov Vasily'  # 0 на счету ОТБОЙ
    # exchange_name = 'ByBit'
    # acc_apikey = 'xTVrkappVmiaDkD9I9'
    # acc_secret = 'Y8vHgcNoZAYeyHBnr78Cp07IXXwRyIebP9NF'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Homiakov Vasily'  # 0 на счету ОТБОЙ
    # exchange_name = 'Mexc'
    # acc_apikey = 'mx0vglr8nTVAt10HTj'
    # acc_secret = '2d773705a862492486ac8b2c4a222ed4'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Poliansky Ruslan'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'lpqRaMG1pLCzVqRKsH'
    # acc_secret = 'PHYq0G046qbb8vrMMlnRJ5GBsSgx9PcoaVBz'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Irvin Andrey Gennagievich'  #
    # exchange_name = 'Mexc'
    # acc_apikey = 'mx0vglhUcrfpj8jjuQ'
    # acc_secret = '878bdf91d7d246f48ebf066c10e20b57'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')
    #
    # account_name = 'Irvin Andrey Gennagievich'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'qK9HbZZgay7aqjTkxS'
    # acc_secret = 'uaPoaJN02WRjR5jK2V8h3CaVgfHFDNZzYAqH'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Novilov Sergey Valentinovich'  #
    # exchange_name = 'ByBit'
    # acc_apikey = 'ivO8bzixCpNTsPDYRb'
    # acc_secret = 'GQN26sfrfmOLJCPpyu2kwVABLVhhd7irILJT'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = 'Maxim'  #
    # exchange_name = 'ByBit'
    # acc_apikey = '2yvIwKC5mjlumriPZV'
    # acc_secret = 'SM4QajjYFMHlNNgks9KxwJUMnERMuO9vkbSs'
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

# --------------------------------------------------------------------------
    account_name = 'Baibotoeva Venera Sragilovna'  # 103 USDT на счету
    exchange_name = 'ByBit'
    acc_apikey = 'g50zbTZ9zZ6ihmGu71'
    acc_secret = 'oaCSavrkm4hRRJQCvA7Q8J3fis97mwL4GwHo'
    print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    account_name = 'Efimov Yury Anatolievich'  # 212 USDT
    exchange_name = 'ByBit'
    acc_apikey = 'MtKsLrYsWgeiMvN7gT'
    acc_secret = 'IYoJEQALoRaYWbzmhyjxUNpEbwO5Wxs5pQ6f'
    print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    account_name = 'Efimov Yury Anatolievich'  # 1660 DEL
    exchange_name = 'Mexc'
    acc_apikey = 'mx0vglGFLBgS7cODQl'
    acc_secret = '2849439de8d34ad59b8ffd0e368a966a'
    print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    # account_name = ''  #
    # exchange_name = 'ByBit'
    # acc_apikey = ''
    # acc_secret = ''
    # print_account_balance(account_name, exchange_name, acc_apikey, acc_secret, acc_password='')

    pass





















