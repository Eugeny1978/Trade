import json
import sqlite3 as sq
import pandas as pd
from data_bases.path_to_base import DATABASE

def get_api_keys(name_account):
    with sq.connect(DATABASE) as connect:
        connect.row_factory = sq.Row  # строки записей в виде dict {}. По умолчанию - кортежи turple ()
        curs = connect.cursor()
        curs.execute("""SELECT * FROM Apikeys WHERE account LIKE ?""", [name_account])
        account = curs.fetchone()
        keys = {'apiKey': account['apikey'], 'secret': account['secret']}
        return keys