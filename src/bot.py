from my_client import Client
import time
import bravado
from dto import *
import configparser


class Bot:
    def __init__(self, client):
        self.client = client
        self.lower_band_order_id = None
        self.upper_band_order_id = None
        self.invest_percentage = 10

        # self.client.cancel_all()
        self.init_bands()

    def init_bands(self):
        print("init bands")

        lower_band_order = client.get_open_order_by_text("lower_band")
        if lower_band_order:
            self.lower_band_order_id = lower_band_order.order_id
        else:
            self.lower_band_order_id = self.create_lower_band_order()

        upper_band_order = client.get_open_order_by_text("upper_band")
        if upper_band_order:
            self.upper_band_order_id = upper_band_order.order_id
        else:
            self.upper_band_order_id = self.create_upper_band_order()

    def create_lower_band_order(self):
        last_price = self.client.get_last_price()
        buy_price = last_price * 0.95
        order_buy = LimitOrderReq.create(Side.BUY, buy_price, self.client.get_available_balance(),
                                         self.invest_percentage, "lower_band")
        lower_band_order = client.submit(order_buy)
        return lower_band_order.order_id

    def create_upper_band_order(self):
        last_price = self.client.get_last_price()
        sell_price = last_price * 1.05
        order_sell = LimitOrderReq.create(Side.SELL, sell_price, self.client.get_available_balance(),
                                          self.invest_percentage, "upper_band")
        upper_band_order = client.submit(order_sell)
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
                sell_price = lower_band_order.price * 1.02
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
                buy_price = upper_band_order.price * 0.98
                last_price = self.client.get_last_price()
                buy_price = min(buy_price, last_price)
                # profit_order = LimitOrderReq.create(Side.BUY, buy_price, self.client.get_available_balance(),
                #                                    self.invest_percentage,
                #                                    "profit_order: " + upper_band_order.order_id)
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


print("starting the bot")
config = configparser.ConfigParser()
config.read("config.ini")
api_key = config["DEFAULT"]["api_key"]
api_secret = config["DEFAULT"]["api_secret"]

client = Client(api_key, api_secret)

print("last price", client.get_last_price())

# exit(0)
while False:
    balance = client.get_available_balance()
    positions = client.get_positions()

    print("-----")
    print(positions)
    print("Available Balance: ", balance)
    client.submit_buy_order(10000, 50)
    sell_power = balance
    buy_power = balance
    # Price can not be ignored
    margin_py_quantity = positions.quantity * client.get_last_price()
    if margin_py_quantity > 0:
        sell_power += math.fabs(margin_py_quantity)
    #   else:
    #      buy_power -= math.fabs(margin_py_quantity)
    print("buy market power: ", buy_power)
    print("Sell market power:", sell_power)

    time.sleep(5)

print("--- STARTING THE BOT ---")
bot = Bot(client)

while True:
    try:
        bot.check_and_update()
        print("[-] INFOS")
        print("[P]", client.get_positions())
        for order in client.get_orders():
            print("[O]", order)

        time.sleep(5)
    except NotEnoughBalanceException:
        print("Not enough balance in the wallet! Cancel all orders")
        # bot.cancel_all_orders()
        time.sleep(10)
    except bravado.exception.HTTPBadRequest as ex:
        print("HTTPBadRequest:", ex)
        time.sleep(10)
