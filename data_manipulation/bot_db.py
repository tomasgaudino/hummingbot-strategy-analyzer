import pandas as pd
import sqlalchemy as db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
# from connectors.kucoin import KucoinConnector


class BotDB:
    def __init__(self, db_engine, db_username, db_password, db_host, db_port, db_name):
        self._db_engine = db_engine
        self._db_username = db_username
        self._db_password = db_password
        self._db_host = db_host
        self._db_port = db_port
        self._db_name = db_name
        self._connected = False
        self._conn = False
        self._engine = False
        self.try_connect()

    def is_connected(self):
        return self._connected

    def connect(self):
        try:
            self._engine = db.create_engine(
                '{}://{}:{}@{}:{}/{}'.format(self._db_engine,
                                             self._db_username,
                                             self._db_password,
                                             self._db_host,
                                             self._db_port,
                                             self._db_name))
            self._conn = self._engine.connect()
            self._connected = True
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            print("Error al conectar con la base de datos")
            print(error)

    def try_connect(self, tries=3):
        count = 0
        while count < tries:
            self.connect()
            if self._connected:
                count = tries
            else:
                count = count + 1

    def get_table(self, table_name):
        metadata = db.MetaData()
        return db.Table(table_name, metadata, autoload=True, autoload_with=self._engine)

    def get_bots_status(self):
        if not self._connected:
            self.try_connect(5)
        bots = self.get_table('TradeFill')
        bots_query = db.select(
            bots.c.config_file_path).where(
            bots.c.market == 'kucoin')
        df = pd.read_sql_query(bots_query, con=self._conn)
        df['active'] = True
        df['trading_pair'] = "HOTCROSS-USDT"
        return df

    def get_trades_stats(self):
        if not self._connected:
            self.try_connect(5)
        tf = self.get_table('TradeFill')
        trades_query = db.select(
            [tf.c.config_file_path,
             tf.c.trade_type,
             db.func.sum(tf.c.amount).label('volume_base'),
             db.func.count().label('trades'),
             db.func.sum(tf.c.amount * tf.c.price).label('volume_quote')]) \
            .group_by(
                tf.c.config_file_path,
                tf.c.trade_type)
        df = pd.read_sql_query(trades_query, self._conn)
        df['avg_price'] = df['volume_quote'] / df['volume_base']
        return df

    # def get_balance_stats(self, base, quote, kucoin_creds):
    #     k = KucoinConnector(kucoin_creds)
    #     balance_query = pd.DataFrame()
    #     df = self.get_bots_timeline()
    #     orders = k.get_balance_history(base, quote)
    #     print(orders.info())
    #     for index, row in df.iterrows():
    #         start = row['start_timestamp']
    #         stop = row['stop_timestamp']
    #         subset = orders[(orders['timestamp'] >= start) & (orders['timestamp'] <= stop)].reset_index().drop(columns=['index'])
    #         if not subset.empty:
    #             dict_balance = {
    #                 'config_file_path': row['config_file_path'],
    #                 'start_balance_base': subset[base].iloc[-1],
    #                 'start_balance_quote': subset[quote].iloc[-1],
    #                 'start_price': subset['price'].iloc[-1],
    #                 'current_balance_base': subset[base].iloc[0],
    #                 'current_balance_quote': subset[quote].iloc[0],
    #                 'current_price': subset['price'].iloc[0]
    #             }
    #             appending = pd.DataFrame([dict_balance])
    #             balance_query = pd.concat([balance_query, appending], axis=0, ignore_index=True)
    #
    #     return balance_query

    def get_orders_cancelled(self):
        if not self._connected:
            self.try_connect(5)
        o = self.get_table('Order')
        trades_query = db.select([o.c.config_file_path,
                                 o.c.creation_timestamp,
                                 o.c.strategy,
                                 o.c.amount,
                                 o.c.leverage,
                                 o.c.last_status,
                                 o.c.price]).where(o.c.market == 'kucoin', o.c.last_status == 'OrderCancelled')
        orders = pd.read_sql_query(trades_query, self._conn)
        orders['date'] = orders['creation_timestamp'].apply(lambda x: datetime.fromtimestamp(x/1000))
        orders['price'] = orders['price']/(10**6)
        orders['amount'] = orders['amount']/(10**6)
        orders['total_usdt'] = orders['price']*orders['amount']
        return orders

    def get_bots_timeline(self):
        if not self._connected:
            self.try_connect(5)
        o = self.get_table('Order')
        trades_query = db.select(
            [o.c.config_file_path,
             o.c.creation_timestamp,
             o.c.strategy]).where(o.c.market == 'kucoin')
        orders = pd.read_sql_query(trades_query, self._conn)
        sorted_orders = orders[['creation_timestamp', 'config_file_path', 'strategy']].sort_values('creation_timestamp')
        strategies_sorted = sorted_orders.config_file_path.drop_duplicates()

        df = pd.DataFrame(columns=['config_file_path', 'start_timestamp', 'stop_timestamp'])
        for strategy in strategies_sorted:
            dict_timeline = {
                'config_file_path': strategy,
                'start_timestamp': sorted_orders[sorted_orders['config_file_path'] == strategy]
                .creation_timestamp.astype('int64').min(),
                'stop_timestamp': sorted_orders[sorted_orders['config_file_path'] == strategy]
                .creation_timestamp.astype('int64').max()
            }
            temp_df = pd.DataFrame([dict_timeline])
            df = pd.concat([df, temp_df], axis=0, ignore_index=True)
        df = df.reset_index().drop(columns=['index'])
        df[['start_timestamp', 'stop_timestamp']] = df[['start_timestamp', 'stop_timestamp']].astype('int64')
        df['start_date'] = df['start_timestamp'].apply(lambda x: datetime.fromtimestamp(x/1000))
        df['stop_date'] = df['stop_timestamp'].apply(lambda x: datetime.fromtimestamp(x/1000))
        return df


