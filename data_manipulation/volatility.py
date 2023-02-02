import pandas as pd


class Volatility:

    def calculate_atr(self, tr_series, tr_periods=14):
        atr_list = [0.000282] # need to get it from exchange, unless you have entire token history
        i = 0
        for index, tr in tr_series[1:].items():
            atr = (atr_list[i] * (tr_periods - 1) + tr) / tr_periods
            atr_list.append(atr)
            i = i + 1
        atr_series = pd.Series(atr_list)
        return atr_series
