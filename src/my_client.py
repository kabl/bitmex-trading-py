import bitmex
import json
import math
from bitmex_websocket import BitMEXWebsocket
from dto import OrderResp
from dto import LimitOrderReq
from dto import PositionResp
from utils import Calc
from utils import SpamProtectionException


upper_band = None
lower_band = None


class Client:
    def __init__(self, api_key, api_secret, main_net=False):
        if main_net:
            raise NotImplementedError("Main net not yet supported")

        self.client = bitmex.bitmex(test=True, api_key=api_key, api_secret=api_secret)
        self.ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v2", symbol="XBTUSD", api_key=api_key, api_secret=api_secret)

    def get_orders(self, incl_closed=False):
        if incl_closed:
            order_filter = None
        else:
            order_filter = json.dumps({"open": True})

        orders = self.client.Order.Order_getOrders(symbol='XBTUSD', reverse=False, filter=order_filter).result()[0]
        orders_dto = []
        for order in orders:
            orders_dto.append(OrderResp(order))

        return orders_dto

    def get_open_order_by_text(self, text):
        open_orders = self.get_orders()
        results = list(filter(lambda o: text in o.text, open_orders))
        if len(results) == 1:
            return results[0]
        else:
            return None

    def get_order_by_id(self, order_id):
        order_filter = json.dumps({"orderID": order_id})
        orders = self.client.Order.Order_getOrders(filter=order_filter).result()[0]
        if len(orders) == 0:
            return None
        return OrderResp(orders[0])

    def get_last_price(self):
        ticker = self.ws.get_instrument()["lastPrice"]
        return ticker

    def submit(self, order: LimitOrderReq):
        print("POST:", order)

        if order.order_value_XBt < Calc.spam_protection_invest_XBt:
            raise SpamProtectionException()

        result = OrderResp(self.client.Order.Order_new(symbol=order.symbol,
                                                       orderQty=order.order_qty,
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
        if math.fabs(orderValueXBt) < Calc.spam_protection_invest_XBt:
            raise SpamProtectionException()

        return OrderResp(self.client.Order.Order_new(symbol='XBTUSD', orderQty=quantity, price=price).result()[0])

    def cancel_order(self, order_id):
        return OrderResp(self.client.Order.Order_cancel(orderID=order_id).result()[0][0])

    def cancel_all(self):
        orders = self.client.Order.Order_cancelAll().result()[0]
        orders_dto = []
        for order in orders:
            orders_dto.append(OrderResp(order))

        return orders_dto

    def submit_sell_order(self, price, quantity):
        return self.submit_buy_order(price, -1 * quantity)

    def submit_leverage(self, leverage):
        # Send 0 to enable cross margin.
        result = self.client.Position.Position_updateLeverage(symbol="XBTUSD", leverage=leverage).result()
        return result

    def get_last_trades(self):
        return self.ws.recent_trades()

    def get_funds(self):
        return self.ws.funds()

    def get_available_balance(self):
        return self.get_funds()["availableMargin"]

    def get_positions(self):
        return PositionResp(self.ws.data['position'][0])

    def get_position_margin(self):
        return self.get_positions()[0]["maintMargin"]

    def get_open_order_margin(self):
        return self.get_positions()[0]["initMargin"]
