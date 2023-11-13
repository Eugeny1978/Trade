import streamlit as st
import ccxt
import json
import pandas as pd
from data_bases.metods import get_api_keys
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np

sns.set_theme(style="whitegrid")

# В терминале набрать:
# streamlit run app.py
st.set_page_config(layout="wide") # Вся страница вместо узкой центральной колонки
# pd.set_option('display.max_rows', 100)



@st.cache_data
def load_exchange():
    api_keys = get_api_keys('Luchnik_Binance_Test_Spot')
    exchange = ccxt.binance(api_keys)
    exchange.set_sandbox_mode(True)
    exchange.load_markets()
    return exchange

symbol = 'ETH/USDT'
exchange = load_exchange()
# tiker = exchange.fetch_ticker(symbol)
order_book = exchange.fetch_order_book(symbol, limit=100)



columnA, columnB, columnC = st.columns([0.12, 0.12, 0.76])
with columnA:
    st.markdown(f'Ордера Asks')
    st.markdown('(готовы Продать)')
    asks = pd.DataFrame(order_book['asks'], columns=('price', 'amount'))
    asks['price'] = asks['price'].map('{:.2f}'.format)
    # st.dataframe(asks.style.background_gradient(cmap='Blues'), hide_index=True)
    # st.dataframe(asks.style.background_gradient(cmap='PuBu'), hide_index=True)
    st.dataframe(asks, hide_index=True)
    st.write(f"Кол-во Слотов: {len(asks)}")
with columnB:
    # st.markdown('График Asks')
    # st.bar_chart(asks, x="price", y='amount', use_container_width=True) #
    st.markdown('Ордера Bids')
    st.markdown('(готовы Купить)')
    bids = pd.DataFrame(order_book['bids'], columns=('price', 'amount'))
    bids['price'] = bids['price'].map('{:.2f}'.format)
    st.dataframe(bids, hide_index=True)
    st.write(f"Кол-во Слотов: {len(bids)}")
with columnC:
    # fig, axes = plt.subplots(3, 1) # , sharex=True, figsize=(10, 5)
    plot_asks = sns.barplot(data=asks, x='amount', y="price", label="Asks", color="red", orient='h', n_boot=100, order=asks['price'].iloc[::-1], width=1)
    plot_bids = sns.barplot(data=bids, x='amount', y="price", label="Bids", color="green", orient='h', n_boot=100, order=bids['price'], width=1)
    plot_asks.set_yticklabels(plot_asks.get_ymajorticklabels()+plot_bids.get_ymajorticklabels(), fontdict={'size': 4})
    plot_bids.set_title('Order Book')
    sns.despine(left=True, bottom=True, right=True, top=True)
    st.pyplot(plot_bids.get_figure())

with columnC:
    plot_a = sns.barplot(data=asks, x='amount', y="price", label="Asks", color="red", orient='h', n_boot=100, order=asks['price'].iloc[::-1], width=1)
    # plot_b = sns.barplot(data=bids, x='amount', y="price", label="Bids", color="green", orient='h', n_boot=100, order=bids['price'], width=1)
    st.pyplot(plot_a.get_figure())







# print(json.dumps(order_book))