import streamlit as st
import data_manipulation.bots_stats as bs
from connectors.kucoin import KucoinConnector
import os
import yaml
import pandas as pd

st.set_page_config(layout='wide')

bots_stats, strategies = bs.get_bots_stats()
grid_bots = bs.get_grid_bots()


def save_uploadedfile(uploadedfile):
    root_dir = os.path.dirname(os.path.dirname(__file__))
    temp_dir = os.path.join(root_dir, 'strategies')
    with open(os.path.join(temp_dir, uploadedfile.name), "wb") as f:
        f.write(uploadedfile.getbuffer())
    return st.success("Saved File:{} to strategies folder. Please, refresh page.".format(uploadedfile.name))


# Title
st.title('Query builder')

# First section
st.subheader('Step 1: Choose your strategy')
col1, col2 = st.columns(2)
with col1:
    strategy_selected = st.radio('Choose your strategy:', strategies)
    new_strategy_file = st.file_uploader('Upload strategy', '.yml')
    if new_strategy_file:
        save_uploadedfile(new_strategy_file)
with col2:
    st.write(bots_stats[strategy_selected])

# Second section
st.subheader('Step 2: Set params')
start_date = st.date_input('Start date')
end_date = st.date_input('End date')

# Third section
st.subheader('Step 3: Auth credentials')
uploaded_creds = st.file_uploader("Drop your .yml file with credentials here", ".yml")

start_query = st.button('Generate query!')

if start_query:

    market = bots_stats[strategy_selected]['market']
    base = market.split('-')[0]
    quote = market.split('-')[1]

    if uploaded_creds is not None:
        loaded_config = yaml.safe_load(uploaded_creds)
        strategy_selected_df = pd.DataFrame(bots_stats[strategy_selected].items(), columns=['key', 'value'])
        k = KucoinConnector(**loaded_config['kucoin'])
        current_price = k.get_current_price(base, quote)
        candles = k.get_candles(start_date, market)
        pnl_hourly, pnl_hourly_negative, pnl_hourly_positive = k.get_pnl_hourly(start_date, base, quote)
        balance_history = k.get_balance_history(start_date, base, quote)
        fills, fills_buy, fills_sell = k.get_fills(start_date)
        # orders_cancelled = p.get_orders_cancelled()
        # bots_timeline = p.get_bots_timeline()

        writer = pd.ExcelWriter('output_example.xlsx', engine='xlsxwriter')
        candles.to_excel(writer, sheet_name='candles')
        pnl_hourly.to_excel(writer, sheet_name='pnl_hourly')
        pnl_hourly_negative.to_excel(writer, sheet_name='pnl_hourly_negative')
        pnl_hourly_positive.to_excel(writer, sheet_name='pnl_hourly_positive')
        balance_history.to_excel(writer, sheet_name='balance_history')
        fills.to_excel(writer, sheet_name='fills')
        fills_buy.to_excel(writer, sheet_name='fills_buy')
        fills_sell.to_excel(writer, sheet_name='fills_sell')
        strategy_selected_df.to_excel(writer, sheet_name='strategy_selected')
        writer.save()

        st.subheader('Download Results')

        with open(writer, 'rb') as f:
            st.download_button(
                label="Download Excel workbook",
                data=f,
                file_name="dashbot.xlsx",
                mime="application/vnd.ms-excel"
            )
    else:
        st.warning('You shold complete credentials_example.yml and throw it into .streamlit folder.')
