import streamlit as st
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

option = st.radio('What are you going to do?', ['I want to run the demo', 'I want to load my own .xlsx'])
if option == 'I want to run the demo':
    start_button = st.button('Start!')
    uploaded_file = 'output_example.xlsx'
elif option == 'I want to load my own .xlsx':
    uploaded_file = st.file_uploader("Drop your file with your results here", ".xlsx")
else:
    uploaded_file = None

if uploaded_file:
    candles = pd.read_excel(uploaded_file, sheet_name='candles')
    pnl_hourly = pd.read_excel(uploaded_file, sheet_name='pnl_hourly')
    pnl_hourly_negative = pd.read_excel(uploaded_file, sheet_name='pnl_hourly_negative')
    pnl_hourly_positive = pd.read_excel(uploaded_file, sheet_name='pnl_hourly_positive')
    balance_history = pd.read_excel(uploaded_file, sheet_name='balance_history')
    fills = pd.read_excel(uploaded_file, sheet_name='fills')
    fills_buy = pd.read_excel(uploaded_file, sheet_name='fills_buy')
    fills_sell = pd.read_excel(uploaded_file, sheet_name='fills_sell')
    strategy_selected_df = pd.read_excel(uploaded_file, sheet_name='strategy_selected')
    strategy_selected = dict(zip(strategy_selected_df['key'], strategy_selected_df['value']))

    with st.sidebar:
        # Header
        st.subheader("Filters")
        # Date picker
        min_date = balance_history['date'].dt.date.min()
        end_date = datetime.date.today() + relativedelta(days=1)
        current_date = min_date
        date_range = st.date_input("Date picker", (current_date, end_date), min_date, end_date)
        # Strategy
        # strategy_selected = st.selectbox("Choose a strategy file", strategies)
        # Operation
        balance_history_filtered = balance_history[balance_history['date'].dt.date.between(date_range[0],
                                                                                           date_range[1],
                                                                                           inclusive='both')]
        candles_filtered = candles[candles['date'].dt.date.between(date_range[0], date_range[1], inclusive='both')]
        fills_filtered = fills[fills['date'].dt.date.between(date_range[0], date_range[1], inclusive='both')]
        fills_buy = fills_filtered[fills_filtered['side'] == 'buy']
        fills_sell = fills_filtered[fills_filtered['side'] == 'sell']
        # orders_cancelled_filtered = orders_cancelled[orders_cancelled['date'].dt.date.between(date_range[0],
        #                                                                                       date_range[1],
        #                                                                                       inclusive='both')]

    # --------------------------- PRE-PORTFOLIO ------------------------------------

    current_portfolio_value = round(balance_history['total_USDT'][0], 2)
    start_portfolio_value = round(balance_history_filtered['total_USDT'].iloc[-1], 2)
    max_portfolio_value = round(balance_history_filtered['total_USDT'].max(), 2)
    min_portfolio_value = round(balance_history_filtered['total_USDT'].min(), 2)
    delta = round(current_portfolio_value - start_portfolio_value, 2)
    if delta > 0:
        delta_sign = "+"
    else:
        delta_sign = "-"
    delta_pct = round(delta * 100 / start_portfolio_value, 2)

    # --------------------------- HEADER LABELS ------------------------------------
    st.title('Dashboard Preview')
    st.subheader('Portfolio stats')
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current portfolio value", f"${current_portfolio_value}", f"{delta_pct}%")
    col2.metric("Start value", f"${start_portfolio_value}")
    col3.metric("Max value", f"${max_portfolio_value}")
    col4.metric("Min value", f"${min_portfolio_value}")

    # ------------------------ PORTFOLIO OVER TIME ------------------------------------

    balance_history_fig = go.Figure(
        [go.Scatter(x=balance_history_filtered['date'], y=balance_history_filtered['total_USDT'])])
    balance_history_fig.update_layout(xaxis_range=[date_range[0], date_range[1]])
    st.plotly_chart(balance_history_fig, use_container_width=True)

    # ---------------------------- CANDLESTICK ----------------------------------------

    st.subheader('Candlestick')

    candles_fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Buy fills
    candles_fig.add_trace(
        go.Scatter(
            mode='markers',
            customdata=np.stack((fills_buy['size'], fills_buy['total_usdt'], fills_buy['fee']), axis=-1),
            x=fills_buy['date'],
            y=fills_buy['price'],
            name='buy filled',
            yaxis='y2',
            opacity=0.5,
            marker=dict(
                symbol='circle',
                size=8,
                color='green',
                line_width=1,
                line_color='white',
            ),
            hovertemplate="date: %{x}<br>side: buy<br>price: %{y:$.4f}<br>size: %{customdata[0]}<br>total_usdt: %{customdata[1]:$.4f}<br>fee: %{customdata[2]:$.4f}<extra></extra>"
        ), secondary_y=False
    )

    # Sell fills
    candles_fig.add_trace(
        go.Scatter(mode='markers',
                   customdata=np.stack((fills_sell['size'], fills_sell['total_usdt'], fills_sell['fee']), axis=-1),
                   x=fills_sell['date'],
                   y=fills_sell['price'],
                   name='sell filled',
                   yaxis='y2',
                   opacity=0.5,
                   marker=dict(
                       symbol='circle',
                       size=8,
                       color='red',
                       line_width=1,
                       line_color='white',
                   ),
                   hovertemplate="date: %{x}<br>side: sell<br>price: %{y:$.4f}<br>size: %{customdata[0]}<br>total_usdt: %{customdata[1]:$.4f}<br>fee: %{customdata[2]:$.4f}<extra></extra>"
                   ), secondary_y=False
    )

    # Cancelled fills
    # candles_fig.add_trace(
    #     go.Scatter(
    #         mode='markers',
    #         customdata=np.stack((orders_cancelled_filtered['amount'], orders_cancelled_filtered['total_usdt']),
    #                             axis=-1),
    #         x=fills_buy['date'],
    #         y=fills_buy['price'],
    #         marker_symbol='circle',
    #         marker_size=8,
    #         marker_color='lightgray',
    #         name='cancelled',
    #         yaxis='y2',
    #         marker_line_width=1,
    #         marker_line_color='white',
    #         opacity=0.8,
    #         hovertemplate="date: %{x}<br>side: buy<br>price: %{y:$.4f}<br>amount: %{customdata[0]}<br>total_usdt: %{customdata[1]:$.4f}<extra></extra>"),
    #     secondary_y=False
    # )

    # Candlestick
    candles_fig.add_trace(
        go.Candlestick(
            x=candles_filtered['date'],
            open=candles_filtered['open'],
            high=candles_filtered['high'],
            low=candles_filtered['low'],
            close=candles_filtered['close'],
            name='Candlestick',
            yaxis='y2'), secondary_y=False)

    # Portfolio base pct

    candles_fig.add_trace(
        go.Scatter(
            x=balance_history['date'],
            y=balance_history['base_pct'],
            fill='tozeroy',
            mode='none',
            name='Base pct (%)',
            opacity=0.4,
            yaxis='y2'
        ),
        secondary_y=True)
    print(strategy_selected)
    # Grid traces
    if strategy_selected['strategy'] == 'fixed_grid':
        candles_fig.add_trace(
            go.Scatter(
                x=(current_date, end_date),
                y=(strategy_selected['grid_price_ceiling'],
                   strategy_selected['grid_price_ceiling']),
                yaxis='y2',
                mode='lines',
                name='grid_price_ceiling',
                opacity=1), secondary_y=False)
        candles_fig.add_trace(
            go.Scatter(
                x=(current_date,
                   end_date),
                y=(strategy_selected['grid_price_floor'],
                   strategy_selected['grid_price_floor']),
                yaxis='y2',
                mode='lines',
                name='grid_price_floor',
                opacity=1), secondary_y=False)

    # Plot
    candles_fig.update_layout(xaxis_range=[date_range[0], date_range[1]])
    st.plotly_chart(candles_fig, use_container_width=True)
    #
    # # ----------------------------- GRID METRICS --------------------------------------
    #
    # if strategy_selected['market'] == 'fixed_grid':
    #     floor = strategy_selected['grid_price_floor']
    #     ceiling = strategy_selected['grid_price_ceiling']
    #     if current_price <= floor:
    #         st.warning('It looks like price went lower than grid floor!')
    #
    #         grid_orders = bs.get_grid_orders(current_bot=grid_bots[strategy_selected])
    #         max_buy_filled_price = fills[fills['date'].dt.date.between(current_date, end_date)]['price'].max()
    #         mbfp_gap = round(max_buy_filled_price - current_price, 4)
    #         mbfp_gap_pct = round((max_buy_filled_price / current_price - 1) * 100, 2)
    #         exit_loss = round(grid_orders['total_usdt'].sum() - current_price * balance_history['BTC'].iloc[0], 4)
    #
    #         col1, col2, col3, col4 = st.columns(4)
    #         col1.metric("Max buy filled price", f"${round(max_buy_filled_price, 4)}")
    #         col2.metric("Current price", f"${round(current_price, 4)}")
    #         col3.metric("Max filled buy gap", f"${mbfp_gap}", f"{mbfp_gap_pct}%")
    #         col4.metric("Exit loss", f"${exit_loss}")
    #     elif (current_price > floor) & (current_price <= ceiling):
    #         st.success("You're making profit!")

    # ---------------------------- AVERAGE TRUE RANGE ----------------------------------
    st.subheader('Average true range')
    atr_fig = go.Figure(
        go.Scatter(
            x=candles_filtered['date'],
            y=candles_filtered['atr_pct'],
            mode='lines',
            name='Average true range (%)'
        )
    )
    atr_fig.update_yaxes(title='ATR (%)', hoverformat='%{y:.3f}')
    st.plotly_chart(atr_fig, use_container_width=True)
    # ---------------------------- PNL OVER TIME ----------------------------------

    st.subheader('PNL over time')
    pnl_fig = go.Figure()

    # Positive pnl
    pnl_fig.add_trace(
        go.Bar(x=pnl_hourly_positive['hr_grouper_date'],
               y=pnl_hourly_positive['t-1'],
               marker=dict(
                   color='red'),
               name='loss'))

    # Negative pnl
    pnl_fig.add_trace(
        go.Bar(x=pnl_hourly_negative['hr_grouper_date'],
               y=pnl_hourly_negative['t-1'],
               marker=dict(
                   color='green'),
               name='win'))

    # Cumulative
    pnl_fig.add_trace(
        go.Scatter(x=pnl_hourly['hr_grouper_date'],
                   y=pnl_hourly['cumsum_t-1'],
                   marker=dict(
                       color='blue'
                   ),
                   name='cum'))

    # Bots shadow + hover
    # for index, row in bots_timeline.iterrows():
    #     name = row['config_file_path']
    #     hoverstats = {''.join(f'{k}: {v}') + '<br>' for k, v in bots_stats[name].items() if v is not None}
    #     hoverstats_text = ""
    #     for stat in hoverstats:
    #         hoverstats_text = hoverstats_text + stat
    #     pnl_fig.add_vrect(x0=row['start_date'],
    #                       x1=row['stop_date'],
    #                       annotation_text=row['config_file_path'],
    #                       annotation_position='top right',
    #                       fillcolor="lightblue",
    #                       opacity=0.2,
    #                       annotation_hovertext=hoverstats_text,
    #                       annotation_textangle=-90)

    # Plot
    pnl_fig.update_layout(xaxis_range=[date_range[0], date_range[1]])
    st.plotly_chart(pnl_fig, use_container_width=True)

