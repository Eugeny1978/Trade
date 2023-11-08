import sqlite3 as sq                            # Библиотека  Работа с БД
from data_bases.path_to_base import DATABASE


with sq.connect(DATABASE) as connect:
    connect.row_factory = sq.Row  # Если хотим строки записей в виде dict {}. По умолчанию - кортежи turple ()
    curs = connect.cursor()

    curs.execute("""SELECT 
account, 
apikey as apiKey, 
secret, 
Accounts.exchange 
FROM Apikeys 
JOIN Accounts ON Accounts.name == Apikeys.account
WHERE Apikeys.name LIKE 'Info'""")
    accounts = curs.fetchall()
    # for row in accounts:
    #     print(row['exchange'])