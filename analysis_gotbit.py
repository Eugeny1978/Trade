import pandas as pd                                  # Объекты DataFrame
import seaborn as sns
from matplotlib import pyplot as plt

pd.options.display.width= None # Отображение Таблицы на весь Экран
pd.options.display.max_columns= 20 # Макс Кол-во Отображаемых Колонок
pd.options.display.max_rows= 20 # Макс Кол-во Отображаемых Колонок
pd.options.display.float_format = '{:.6f}'.format # Формат отображения Чисел float
dividing_line = '-------------------------------------------------------------------------------------'
double_line =   '====================================================================================='

if __name__ == '__main__':
    path_to_file = 'E:/РАБОТА/MEXC Gotbit DELUSDT 2024_01_06.csv'
    data = pd.read_csv(path_to_file, delimiter=';')
    data['create_time'] = data['create_time'].astype('datetime64[ns]')
    # data.info()
    data = data[data['create_time'] < '2023-12-20']
    # print(data)

    buy_data = data.query(f'side == "BUY"').copy().reset_index()[['price', 'quantity', 'amount_usdt']]
    sell_data = data.query(f'side == "SELL"').copy().reset_index()[['price', 'quantity', 'amount_usdt']]
    # print(buy_data, sell_data, sep='\n')

    sum_quantity_buy = round(buy_data['quantity'].sum())
    sum_usdt_buy = round(buy_data['amount_usdt'].sum())
    sum_quantity_sell = round(sell_data['quantity'].sum())
    sum_usdt_sell = round(sell_data['amount_usdt'].sum())

    deals = pd.DataFrame(columns=['side', 'DEL_amount', 'USDT_amount', 'price'])
    deals.loc[len(deals)] = ['BUYs', sum_quantity_buy, sum_usdt_buy, round(sum_usdt_buy / sum_quantity_buy, 6)]
    deals.loc[len(deals)] = ['SELLs', sum_quantity_sell, sum_usdt_sell, round(sum_usdt_sell / sum_quantity_sell, 6)]
    quantity_delta = sum_quantity_buy - sum_quantity_sell
    usdt_delta = sum_usdt_buy - sum_usdt_sell
    price_delta = round(usdt_delta / quantity_delta, 6)
    deals.loc[len(deals)] = ['Result', quantity_delta, usdt_delta, price_delta]
    print(deals)
    print('ВЫВОД:', f'Приобрели DEL: {quantity_delta} | Потратили USDT: {usdt_delta} | Средняя Цена покупки: {price_delta}', sep='\n')

    buy_group_data = buy_data.groupby('price').sum()
    buy_group_data = buy_group_data.sort_values('price').reset_index()
    # print(buy_group_data)

    sell_group_data = sell_data.groupby('price').sum()
    sell_group_data = sell_group_data.sort_values('price').reset_index()
    # print(sell_group_data)

    fig = plt.figure(figsize=(12, 6), dpi=80)  # figsize=(size_h, size_v)
    gs = fig.add_gridspec(1, 2)
    sns.set_theme(style="whitegrid")
    sns.axes_style("darkgrid")

    fig.add_subplot(gs[0, 0])
    sns.histplot(data=buy_group_data, y='amount_usdt', x='price', color="green", bins=100, element='bars').set_title('BUYs')
    # sns.barplot(data=buy_group_data, y='amount_usdt', x='price', label="BUYs", color="green", bins=100).set_title('BUYs')

    fig.add_subplot(gs[0, 1])
    sns.histplot(data=sell_group_data, y='amount_usdt', x='price', color="red", bins=100).set_title('SELLs')

    sns.despine(left=True, bottom=True, right=True, top=True)
    plt.show()


