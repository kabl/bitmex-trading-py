import bitmex
import json
from bitmex_websocket import BitMEXWebsocket
from Utils import *
import math
from Order_dto import *


upper_band = None
lower_band = None


class Client:
    def __init__(self, api_key, api_secret):
        self.client = bitmex.bitmex(test=True)
        self.ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v2", symbol="XBTUSD", api_key=api_key, api_secret=api_secret)

    def get_orders(self, all_orders=False):
        if all_orders:
            order_filter = None
        else:
            order_filter = json.dumps({"open": True})

        orders = self.client.Order.Order_getOrders(symbol='XBTUSD', reverse=False, filter=order_filter).result()[0]
        orders_dto = []
        for order in orders:
            orders_dto.append(OrderDto(order))

        return orders_dto

    def get_order_by_id(self, order_id):
        order_filter = json.dumps({"orderID": order_id})
        orders = self.client.Order.Order_getOrders(filter=order_filter).result()[0]
        if len(orders) == 0:
            return None
        return OrderDto(orders[0])

    def get_last_price(self):
        ticker = self.ws.get_instrument()["lastPrice"]
        return ticker

    def submit(self, order: LimitOrder):
        print("POST:", order)

        if order.order_value_XBt < Calc.spam_protection_invest_XBt:
            raise SpamProtectionException()

        result = OrderDto(self.client.Order.Order_new(symbol=order.symbol,
                                        orderQty=order.quantity,
                                        price=order.price,
                                        side=order.side,
                                        text=order.text,
                                        ordType=order.order_type).result()[0])
        print("POST Result", result)
        return result

    def submit_buy_order(self, price, quantity):
        price = round(price * 2) / 2 #rounding to x.0 or x.5
        quantity = round(quantity, 0)
        orderValueXBt = (quantity / price) * 100000000
        print("submit order price:", price)
        print("submit order quantity", quantity)
        print("order value XBT:", orderValueXBt)
        if math.fabs(orderValueXBt) < 250000:
            raise SpamProtectionException()

        return OrderDto(self.client.Order.Order_new(symbol='XBTUSD', orderQty=quantity, price=price).result()[0])

    def cancel_order(self, order_id):
        return OrderDto(self.client.Order.Order_cancel(orderID=order_id).result()[0][0])

    def cancel_all(self):
        orders = self.client.Order.Order_cancelAll().result()[0]
        orders_dto = []
        for order in orders:
            orders_dto.append(OrderDto(order))

        return orders_dto

    def submit_sell_order(self, price, quantity):
        return self.submit_buy_order(price, -1 * quantity)

    def get_last_trades(self):
        return self.ws.recent_trades()

    def get_funds(self):
        return self.ws.funds()

    def get_available_balance(self):
        return self.get_funds()["availableMargin"]

    def get_positions(self):
        return self.ws.data['position']

    def get_position_margin(self):
        return self.get_positions()[0]["maintMargin"]

    def get_open_order_margin(self):
        return self.get_positions()[0]["initMargin"]
