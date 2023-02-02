from yaml import load, FullLoader
import os
import pandas as pd
import numpy as np


def get_filenames_from_path(path):
    f = []
    for root, dirnames, filenames in os.walk(path):
        f.extend(filenames)
        break
    f.sort()
    if f == list():
        return None
    else:
        return f


def get_bots_stats(strategies_folder='strategies'):
    root_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(root_dir, strategies_folder)
    strategies = get_filenames_from_path(path)
    if strategies is not None:
        bots_stats = dict()
        for strategy in strategies:
            path_strategy = os.path.join(path, strategy)
            with open(path_strategy) as file:
                bots_stats[strategy] = load(file, FullLoader)
        return bots_stats, strategies
    else:
        return None


def get_grid_bots():
    stats, strategies = get_bots_stats()
    df = pd.DataFrame(stats).transpose()
    df = df[df['strategy'] == 'fixed_grid']
    df = df.transpose().dropna()
    return df


def get_grid_orders(current_bot):
    grid_price_floor = current_bot['grid_price_floor']
    grid_price_ceiling = current_bot['grid_price_ceiling']
    n_levels = current_bot['n_levels']
    grid_range = grid_price_ceiling - grid_price_floor
    orders_price = np.arange(grid_price_floor, grid_price_ceiling, grid_range/n_levels)
    grid_orders = pd.DataFrame(orders_price, columns=['price'])
    grid_orders['amount'] = current_bot['order_amount']
    grid_orders['total_usdt'] = grid_orders['price'] * grid_orders['amount']
    return grid_orders
