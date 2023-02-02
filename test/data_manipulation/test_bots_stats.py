import unittest

import data_manipulation.bots_stats
import data_manipulation.bots_stats as bs
import os
from unittest.mock import patch


class TestBotStats(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('setupClass')

    @classmethod
    def tearDownClass(cls):
        print('teardownClass')

    def setUp(self):
        self.path_strategies = os.path.join(os.pardir, 'strategy_examples')
        self.strategies = ['01_strategy.yml', '02_strategy.yml', '03_strategy.yml']
        self.root_dir = os.path.dirname(os.path.abspath("setup.py"))
        self.bots_stats = {'01_strategy.yml': {'template_version': 22, 'strategy': 'fixed_grid', 'exchange': 'kucoin', 'market': 'HOTCROSS-USDT', 'n_levels': 50, 'grid_price_ceiling': 0.0205, 'grid_price_floor': 0.0185, 'start_order_spread': 0.2, 'order_refresh_time': 1800.0, 'max_order_age': 1800.0, 'order_refresh_tolerance_pct': 0.0, 'order_amount': 150.0, 'order_optimization_enabled': False, 'ask_order_optimization_depth': 0, 'bid_order_optimization_depth': 0, 'take_if_crossed': True, 'should_wait_order_cancel_confirmation': True}, '02_strategy.yml': {'template_version': 22, 'strategy': 'fixed_grid', 'exchange': 'kucoin', 'market': 'HOTCROSS-USDT', 'n_levels': 40, 'grid_price_ceiling': 0.023, 'grid_price_floor': 0.02, 'start_order_spread': 0.05, 'order_refresh_time': 1800.0, 'max_order_age': 1800.0, 'order_refresh_tolerance_pct': 0.0, 'order_amount': 150.0, 'order_optimization_enabled': False, 'ask_order_optimization_depth': 0.0, 'bid_order_optimization_depth': 0.0, 'take_if_crossed': True, 'should_wait_order_cancel_confirmation': True}, '03_strategy.yml': {'template_version': 22, 'strategy': 'fixed_grid', 'exchange': 'kucoin', 'market': 'HOTCROSS-USDT', 'n_levels': 40, 'grid_price_ceiling': 0.0226, 'grid_price_floor': 0.0196, 'start_order_spread': 0.2, 'order_refresh_time': 1800.0, 'max_order_age': 1800.0, 'order_refresh_tolerance_pct': 0.0, 'order_amount': 150.0, 'order_optimization_enabled': False, 'ask_order_optimization_depth': 0, 'bid_order_optimization_depth': 0, 'take_if_crossed': True, 'should_wait_order_cancel_confirmation': True}}

    def test_get_files_from_path(self):
        self.assertEqual(bs.get_filenames_from_path(self.path_strategies), self.strategies)
        self.assertIsNone(bs.get_filenames_from_path('random_non_existing_path'))

    def test_get_bots_stats(self):
        self.assertEqual(bs.get_bots_stats('test/strategy_examples')[0], self.bots_stats)
        self.assertEqual(bs.get_bots_stats('test/strategy_examples')[1], self.strategies)
        self.assertIsNone(bs.get_bots_stats('random_non_existing_path'))


if __name__ == '__main__':
    unittest.main()
