import logging
from bitmexclient import Client
import dto
import traderconfig


class Bot:
    def __init__(self, client: Client, config: traderconfig.Config):
        self.client = client
        self.config = config
        self.lower_band_order_id = None
        self.upper_band_order_id = None

    def init_bands(self):
        logging.info("init bands")

        lower_band_order = self.client.get_open_order_by_text("lower_band")
        if lower_band_order:
            self.lower_band_order_id = lower_band_order.order_id
            logging.info(f"Use existing lower band: {self.lower_band_order_id}")
        else:
            self.lower_band_order_id = self.create_lower_band_order()
            logging.info(f"Lower Band not active. Created new one: {self.lower_band_order_id}")

        upper_band_order = self.client.get_open_order_by_text("upper_band")
        if upper_band_order:
            self.upper_band_order_id = upper_band_order.order_id
            logging.info(f"Use existing upper band: {self.upper_band_order_id}")
        else:
            self.upper_band_order_id = self.create_upper_band_order()
            logging.info(f"Upper Band not active. Created new one: {self.upper_band_order_id}")

    def check_and_update(self):
        lower_band_order = self.client.get_order_by_id(self.lower_band_order_id)

        if lower_band_order:
            if lower_band_order.order_status == "Filled":
                logging.info(f"Lower band Filled: {lower_band_order}")
                self.lower_band_order_id = self.create_lower_band_order()

                sell_price = lower_band_order.price * (1 + (self.config.take_profit_pc / 100))
                last_price = self.client.get_price().last_price
                sell_price = max(sell_price, last_price)
                profit_order = dto.LimitOrderReq.create_sell_higher(lower_band_order, sell_price)
                self.client.submit(profit_order)

            if lower_band_order.order_status == "Canceled":
                logging.warning(f"Lower band Canceled: {lower_band_order}")
                self.lower_band_order_id = self.create_lower_band_order()

        else:
            logging.warning("No lower band order found. Create new one")
            self.lower_band_order_id = self.create_lower_band_order()

        upper_band_order = self.client.get_order_by_id(self.upper_band_order_id)
        if upper_band_order:
            if upper_band_order.order_status == "Filled":
                logging.info(f"Upper band Filled: {upper_band_order}")
                self.upper_band_order_id = self.create_upper_band_order()

                buy_price = upper_band_order.price * (1 - (self.config.take_profit_pc / 100))
                last_price = self.client.get_price().last_price
                buy_price = min(buy_price, last_price)
                profit_order = dto.LimitOrderReq.create_buy_lower(upper_band_order, buy_price)
                self.client.submit(profit_order)

            if upper_band_order.order_status == "Canceled":
                logging.warning(f"Upper band Canceled: {upper_band_order}")
                self.upper_band_order_id = self.create_upper_band_order()

        else:
            logging.warning("No upper band order found. Create new one")
            self.upper_band_order_id = self.create_upper_band_order()

    def create_lower_band_order(self):
        last_price = self.client.get_price().last_price
        buy_price = last_price * (1 - (self.config.band_pc / 100))
        order_buy = dto.LimitOrderReq.create(dto.Side.BUY,
                                             buy_price,
                                             self.client.get_wallet().available_balance,
                                             self.config.order_size_pc,
                                             "lower_band")
        lower_band_order = self.client.submit(order_buy)
        logging.info(f"New lower band order: {lower_band_order}")
        return lower_band_order.order_id

    def create_upper_band_order(self):
        last_price = self.client.get_price().last_price
        sell_price = last_price * (1 + (self.config.band_pc / 100))
        order_sell = dto.LimitOrderReq.create(dto.Side.SELL,
                                              sell_price,
                                              self.client.get_wallet().available_balance,
                                              self.config.order_size_pc,
                                              "upper_band")
        upper_band_order = self.client.submit(order_sell)
        logging.info(f"New upper band order: {upper_band_order}")
        return upper_band_order.order_id

    # Not used
    def cancel_bands(self):
        logging.info("cancel upper and lower bands")
        if self.lower_band_order_id:
            self.client.cancel_order(self.lower_band_order_id)

        if self.upper_band_order_id:
            self.client.cancel_order(self.upper_band_order_id)

    def cancel_all_orders(self):
        self.client.cancel_all()