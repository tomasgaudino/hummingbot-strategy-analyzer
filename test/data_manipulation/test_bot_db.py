import unittest
import datetime
from connectors.kucoin import KucoinConnector
from unittest.mock import patch
import requests
from dateutil.relativedelta import relativedelta
import os
from dotenv import load_dotenv
class TestBotStats(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('setupClass')

    @classmethod
    def tearDownClass(cls):
        print('teardownClass')

    def setUp(self):
        # self.path_strategies = os.path.join(os.pardir, 'strategy_examples')
        # self.strategies = ['01_strategy.yml', '02_strategy.yml', '03_strategy.yml']
        # self.root_dir = os.path.dirname(os.path.abspath("setup.py"))
        load_dotenv()
        self.symbol = 'BTC-USDT'
        self.base = 'BTC'
        self.quote = 'USDT'
        self._kucoin_connector = KucoinConnector(os.getenv('API_KEY'),
                                                 os.getenv('API_SECRET'),
                                                 os.getenv('API_PASSPHRASE'))

    def test_get_current_price(self):
        with patch('data_manipulation.bot_db.requests.request') as mock_get:
            mock_get.return_value.ok = True
            current_price = self._kucoin_connector.get_current_price(self.base, self.quote)
            mock_get.assert_called_with('get', f'https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={self.base}-{self.quote}')
            self.assertGreaterEqual(current_price, 0)

            mock_get.return_value.ok = False
            mock_get.assert_called_with('get', f'https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={self.base}-{self.quote}')
            self.assertRaises(requests.exceptions.RequestException)

    def test_get_candles(self):
        so_far_away = int(datetime.datetime.timestamp((datetime.datetime(2100, 1, 1, 0, 0, 0))))
        self.assertIsNone(self._kucoin_connector.get_candles(so_far_away, self.symbol))

    def test_get_fills(self):
        # so_far_away = datetime.date(2100, 1, 1)
        # self.assertIsNone(self._kucoin_connector.get_fills(so_far_away))

        week_ago = datetime.datetime.today() - relativedelta(days=14)
        self.assertIsNotNone(self._kucoin_connector.get_fills(week_ago))


if __name__ == '__main__':
    unittest.main()
