from my_client import Client
import time
from dto import *
from Utils import *
import bravado
from dto import *
import configparser


class Bot:
    def __init__(self, client):
        self.client = client
        self.lower_band_order_id = None
        self.upper_band_order_id = None
        self.invest_percentage = 0.2
        self.spam_protection_invest = 250000

        self.client.cancel_all()
        self.init_bands()

    def init_bands(self):
        print("init bands")
        last_price = self.client.get_last_price()

        buy_price = last_price - 0.5 # - 0.5
        order_buy = LimitOrderReq.create(Side.BUY, buy_price, self.client.get_available_balance(), self.invest_percentage, "Lower Band")
        lower_band_order = client.submit(order_buy)
        self.lower_band_order_id = lower_band_order.order_id

        sell_price = last_price + 0.5 # 0.5
        order_sell = LimitOrderReq.create(Side.SELL, sell_price, self.client.get_available_balance(), self.invest_percentage, "Upper Band")
        upper_band_order = client.submit(order_sell)
        self.upper_band_order_id = upper_band_order.order_id

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
        upper_band_order = self.client.get_order_by_id(self.upper_band_order_id)
        reset = False

        if lower_band_order:
            if lower_band_order.order_status == "Filled":
                print("lower band filled:", lower_band_order)
                sell_price = lower_band_order.price * 1.05
                # todo validate sell price is higher than current price
                new_order = LimitOrderReq.create(Side.SELL, sell_price, self.client.get_available_balance(),
                                                 self.invest_percentage, "Profit from: " + lower_band_order.order_id)
                self.client.submit(new_order)
                reset = True

            if lower_band_order.order_status == "Canceled":
                print("Lower band was canceled")
                reset = True

        if upper_band_order:
            if upper_band_order.order_status == "Filled":
                buy_price = upper_band_order.price * 0.95
                new_order = LimitOrderReq.create(Side.BUY, buy_price, self.client.get_available_balance(),
                                                 self.invest_percentage, "Profit from: " + upper_band_order.order_id)
                self.client.submit(new_order)
                reset = True

            if upper_band_order.order_status == "Canceled":
                print("Upper band was canceled")
                reset = True

        if reset:
            print("Reset is true.")
            self.cancel_bands()
            self.init_bands()


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

