from my_client import Client
import time
import bravado
from dto import *
from config import Config


class Bot:
    def __init__(self, client: Client, config: Config):
        self.client = client
        self.config = config
        self.lower_band_order_id = None
        self.upper_band_order_id = None

    def init_bands(self):
        print("init bands")

        lower_band_order = self.client.get_open_order_by_text("lower_band")
        if lower_band_order:
            self.lower_band_order_id = lower_band_order.order_id
        else:
            self.lower_band_order_id = self.create_lower_band_order()

        upper_band_order = self.client.get_open_order_by_text("upper_band")
        if upper_band_order:
            self.upper_band_order_id = upper_band_order.order_id
        else:
            self.upper_band_order_id = self.create_upper_band_order()

    def create_lower_band_order(self):
        last_price = self.client.get_last_price()
        buy_price = last_price * (1 - (self.config.band_pc / 100))
        order_buy = LimitOrderReq.create(Side.BUY, buy_price, self.client.get_available_balance(),
                                         self.config.order_size_pc, "lower_band")
        lower_band_order = self.client.submit(order_buy)
        return lower_band_order.order_id

    def create_upper_band_order(self):
        last_price = self.client.get_last_price()
        sell_price = last_price * (1 + (self.config.band_pc / 100))
        order_sell = LimitOrderReq.create(Side.SELL, sell_price, self.client.get_available_balance(),
                                          self.config.order_size_pc, "upper_band")
        upper_band_order = self.client.submit(order_sell)
        return upper_band_order.order_id

    def cancel_bands(self):
        print("cancel bands")
        if self.lower_band_order_id:
            self.client.cancel_order(self.lower_band_order_id)

        if self.upper_band_order_id:
            self.client.cancel_order(self.upper_band_order_id)

    def cancel_all_orders(self):
        self.client.cancel_all()

    def check_and_update(self):
        lower_band_order = self.client.get_order_by_id(self.lower_band_order_id)
        lower_band_closed = False
        if lower_band_order:
            if lower_band_order.order_status == "Filled":
                print("lower band filled:", lower_band_order)
                sell_price = lower_band_order.price * (1 + (self.config.take_profit_pc / 100))
                last_price = self.client.get_last_price()
                sell_price = max(sell_price, last_price)
                profit_order = LimitOrderReq.create_sell_higher(lower_band_order, sell_price)

                self.client.submit(profit_order)
                lower_band_closed = True

            if lower_band_order.order_status == "Canceled":
                print("Lower band was canceled")
                lower_band_closed = True

            if lower_band_closed:
                print("Lower band closed. Create new lower band order")
                self.lower_band_order_id = self.create_lower_band_order()
        else:
            print("No lower band order found. Create new lower band order")
            self.lower_band_order_id = self.create_lower_band_order()

        upper_band_order = self.client.get_order_by_id(self.upper_band_order_id)
        upper_band_closed = False
        if upper_band_order:
            if upper_band_order.order_status == "Filled":
                buy_price = upper_band_order.price * (1 - (self.config.take_profit_pc / 100))
                last_price = self.client.get_last_price()
                buy_price = min(buy_price, last_price)
                profit_order = LimitOrderReq.create_buy_lower(upper_band_order, buy_price)

                self.client.submit(profit_order)
                upper_band_closed = True

            if upper_band_order.order_status == "Canceled":
                print("Upper band was canceled")
                upper_band_closed = True

            if upper_band_closed:
                print("Upper band closed. Create new upper band order")
                self.upper_band_order_id = self.create_upper_band_order()
        else:
            print("No upper band order found. Create new upper band order")
            self.upper_band_order_id = self.create_upper_band_order()
