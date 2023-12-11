import os

# # Имя Файла Базы Данных (БД)
# base_name = 'DataBase.db'
# # Папка данного файла. В этой же папке находится и файл БД
# folder = os.path.dirname(repr(__file__)).replace("'", '')
#
# # PATH = folder + '\\\\' + base_name # тоже работает, но предпочел чтобы с одной чертой
# path_to_file = (folder + '\\\\' + base_name)
# DATABASE = rf'{path_to_file}'.replace('\\\\', '/')
# # print(DATABASE)

db_name = 'DataBase.db'
db_dir = os.path.dirname(__file__)
DATABASE = os.path.join(db_dir, db_name)
# print(DATABASE)

