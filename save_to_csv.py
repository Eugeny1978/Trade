import pandas as pd

if __name__ == '__main__':
    dir_name = 'E:/РАБОТА/'
    file_name = 'MEXC Gotbit DELUSDT 2024_01_06.csv'
    new_file_name = 'MEXC_DELUSDT_2023_01_06_2023_12_19.csv'
    path_to_file = dir_name + file_name
    path_to_new_file = dir_name + new_file_name

    data = pd.read_csv(path_to_file, delimiter=';')
    data['create_time'] = data['create_time'].astype('datetime64[ns]')
    data = data[data['create_time'] < '2023-12-20']

    data.to_csv(path_to_new_file, sep=';')

