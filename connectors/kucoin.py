import requests
import time
from datetime import datetime
import pandas as pd
import arrow
from urllib.parse import urlencode
from data_manipulation.volatility import Volatility
from time import sleep
import math
import base64
import hmac
import hashlib


class KucoinConnector:
    def __init__(self, api_secret, api_key, api_passphrase):

        self.api_secret = api_secret
        self.api_key = api_key
        self.api_passphrase = api_passphrase

    def get_headers(self, str_to_sign):
        now = int(time.time() * 1000)
        signature = base64.b64encode(
            hmac.new(self.api_secret.encode('utf-8'),
                     str_to_sign.encode('utf-8'),
                     hashlib.sha256).digest())
        passphrase = base64.b64encode(
            hmac.new(self.api_secret.encode('utf-8'),
                     self.api_passphrase.encode('utf-8'),
                     hashlib.sha256).digest())
        headers = {
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": str(now),
            "KC-API-KEY": self.api_key,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": "2"
        }
        return headers

    def get_current_price(self, base, quote):
        try:
            response = requests.request('get',
                                        f'https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={base}-{quote}')
            current_price = float(response.json()['data']['price'])
            return current_price
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def get_candles(self, start_at, market, tr_periods=14):
        v = Volatility()
        interval = 86400
        date_format = 'YYYY-MM-DD HH:mm:ss'
        now = int(time.time())
        start_at_timestamp = int(datetime.timestamp(datetime.combine(start_at, datetime.min.time())))
        if int(start_at_timestamp) <= now:
            # session = requests.Session()
            candles = pd.DataFrame()
            num_periods = math.ceil((now - start_at_timestamp) / interval)
            for period in range(0, num_periods):
                params = {
                    'symbol': market,
                    'type': '1hour',
                    'startAt': start_at_timestamp + interval * period,
                    'endAt': start_at_timestamp + interval * (period+1)}
                url = 'https://api.kucoin.com/api/v1/market/candles?' + urlencode(params)
                response = requests.get(url)
                if response.ok:
                    data = response.json()['data']
                    temp = pd.DataFrame(data, columns=['time', 'open', 'close', 'high', 'low', 'volume', 'turnover'])
                    temp.time = temp.time.astype('int64')
                    temp = temp.sort_values('time')
                    temp['creation_date'] = temp.time.apply(lambda x: arrow.get(x).shift(hours=-3).format(date_format))
                    temp['date'] = temp.creation_date.apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
                    temp['volume_pct_change'] = temp['volume'].astype('float').pct_change()
                    temp['turnover_pct_change'] = temp['turnover'].astype('float').pct_change()
                    candles = pd.concat([candles, temp], axis=0, ignore_index=True)
                else:
                    break
            if not candles.empty:
                candles[['open', 'close', 'high', 'low', 'volume']] = candles[['open', 'close', 'high', 'low', 'volume']].astype('float')

                # VOLATILITY
                # Average true range
                candles['tr_a'] = candles['high'] - candles['low']
                candles['tr_b'] = abs(candles['high'] - candles['close'].shift(1))
                candles['tr_c'] = abs(candles['low'] - candles['close'].shift(1))
                candles['true_range'] = candles[['tr_a', 'tr_b', 'tr_c']].max(axis=1)
                candles['atr'] = v.calculate_atr(candles['true_range'])
                candles['atr_pct'] = candles['atr']*100/candles['close'].shift(1)

                sleep(0.5)
                return candles
            else:
                return None
        else:
            return None

    def get_fills(self, start_at):
        interval = 604800000
        now = int(time.time()*1000)  # 8 Sep 2022 00:00hs
        start_at_timestamp = int(datetime.timestamp(datetime.combine(start_at, datetime.min.time())))*1000
        if int(start_at_timestamp) <= now:
            fills = pd.DataFrame(columns=['size', 'price', 'fee', 'createdAt'])
            num_periods = math.ceil((now - start_at_timestamp) / interval)
            for period in range(0, num_periods + 1):
                page = 1
                while True:
                    params = {
                        'startAt': start_at_timestamp + 604800000 * period,
                        'currentPage': page,
                        'pageSize': 500}
                    url = 'https://api.kucoin.com/api/v1/fills'
                    now = int(time.time()*1000)
                    str_to_sign = str(now) + 'GET' + '/api/v1/fills?' + urlencode(params)
                    headers = self.get_headers(str_to_sign)
                    response = requests.request('get',
                                                url,
                                                params=params,
                                                headers=headers)
                    if response.status_code == 200:
                        data = response.json()['data']['items']
                        if data:
                            temp = pd.DataFrame(data)
                            temp[['size', 'price', 'fee', 'createdAt']] = temp[['size', 'price', 'fee', 'createdAt']].astype('float')
                            fills = pd.concat([fills, temp], axis=0, ignore_index=True)
                        else:
                            break
                    else:
                        break
                sleep(0.5)
                page += 1
            if not fills.empty:
                fills['date'] = fills['createdAt'].apply(lambda x: datetime.fromtimestamp(x / 1000))
                fills['total_usdt'] = fills['size'] * fills['price']
                fills_buy = fills[fills['side'] == 'buy']
                fills_sell = fills[fills['side'] == 'sell']
                return fills, fills_buy, fills_sell
            else:
                return None
        else:
            return None

    def get_portfolio_status(self):
        # Define API params
        url = 'https://api.kucoin.com/api/v1/accounts'
        now = int(time.time() * 1000)
        str_to_sign = str(now) + 'GET' + '/api/v1/accounts'

        # Get response data
        response = requests.request('get', url, headers=self.get_headers(str_to_sign))
        portfolio_data = response.json()['data']
        return portfolio_data

    def get_balance_history(self, start_at, base, quote):
        """
        Build starter row: base amount, quote amount, timestamp, price
        Run penalty recursive loop.
        """
        # Build starter row
        portfolio_data = self.get_portfolio_status()
        current_balance = pd.DataFrame(portfolio_data)
        # Show only trades (avoid main and futures)
        current_balance = current_balance[current_balance['type'] == 'trade']
        # Dict every currency balance and append 2 key-value pairs: current timestamp and current price
        current_balance_dict = dict(zip(current_balance['currency'], current_balance['balance']))
        current_balance_dict['timestamp'] = int(round(time.time() * 1000))
        current_balance_dict['price'] = self.get_current_price(base, quote)
        # Initialize df with first row and set correct dtypes
        current_balance_df = pd.DataFrame([current_balance_dict])
        current_balance_df[base] = current_balance_df[base].astype('float')
        current_balance_df[quote] = current_balance_df[quote].astype('float')

        # Get fills
        df_fill = self.get_fills(start_at)[0]
        df_fill.sort_values('createdAt', ascending=False, inplace=True)

        # Initialize vars from dict: price, base_balance and quote_balance
        price = current_balance_dict['price']
        base_balance = float(current_balance_dict[base])
        quote_balance = float(current_balance_dict[quote])

        # Start loop. Signs are inverted because it goes from now to past. Fee MUST BE always positive.
        for index, row in df_fill.iterrows():
            if row['side'] == "buy":
                base_balance = base_balance - row['size']
                quote_balance = quote_balance + row['size'] * row['price'] + row['fee']
            elif row['side'] == "sell":
                base_balance = base_balance + row['size']
                quote_balance = quote_balance - row['size'] * row['price'] + row['fee']
            appending = pd.DataFrame([{
                'timestamp': row['createdAt'],
                'price': row['price'],
                base: base_balance,
                quote: quote_balance
            }])
            current_balance_df = pd.concat([current_balance_df, appending], axis=0, ignore_index=True)

        # Save balance history to new df
        balance_history = current_balance_df.reset_index().drop(columns=['index'])
        balance_history['base_USDT'] = balance_history[base] * balance_history['price']
        balance_history['total_USDT'] = balance_history[quote] + balance_history['base_USDT']
        balance_history['date'] = balance_history['timestamp'].apply(lambda x: datetime.fromtimestamp(x/1000))
        balance_history['hr_grouper'] = balance_history['date'].dt.strftime("%Y-%m-%d, %H:00:00")
        balance_history['base_pct'] = balance_history['base_USDT']*100/balance_history['total_USDT']
        return balance_history

    def get_pnl_hourly(self, start_at, base, quote):
        balance_history = self.get_balance_history(start_at, base, quote)
        pnl_hourly = balance_history.groupby('hr_grouper')['total_USDT'].mean().reset_index()
        pnl_hourly['t-1'] = pnl_hourly['total_USDT'] - pnl_hourly['total_USDT'].shift(1)
        pnl_hourly['cumsum_t-1'] = pnl_hourly['t-1'].cumsum()
        pnl_hourly['hr_grouper_date'] = pnl_hourly['hr_grouper'].apply(
            lambda x: datetime.strptime(x, "%Y-%m-%d, %H:%M:%S"))
        pnl_hourly_positive = pnl_hourly[pnl_hourly['t-1'] < 0]
        pnl_hourly_negative = pnl_hourly[pnl_hourly['t-1'] > 0]
        return pnl_hourly, pnl_hourly_negative, pnl_hourly_positive
