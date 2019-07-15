import logging
import json
import bitmex
from bitmex_websocket import BitMEXWebsocket
import dto
import utils


class Client:
    def __init__(self, api_key, api_secret, main_net=False):
        if main_net:
            raise NotImplementedError("Main net not yet supported")

        self.client = bitmex.bitmex(test=True, api_key=api_key, api_secret=api_secret)
        self.ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v2", symbol="XBTUSD", api_key=api_key,
                                  api_secret=api_secret)

    def get_orders(self, incl_closed=False):
        if incl_closed:
            order_filter = None
        else:
            order_filter = json.dumps({"open": True})

        orders = self.client.Order.Order_getOrders(symbol='XBTUSD', reverse=False, filter=order_filter).result()[0]
        orders_dto = []
        for order in orders:
            orders_dto.append(dto.OrderResp(order))

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
        return dto.OrderResp(orders[0])

    def get_last_price(self):
        ticker = self.ws.get_instrument()["lastPrice"]
        return ticker

    def submit(self, order: dto.LimitOrderReq):
        logging.info(f"Submit order: {order}")

        if order.order_value_XBt < utils.Calc.spam_protection_invest_XBt:
            raise utils.SpamProtectionException()

        result = dto.OrderResp(self.client.Order.Order_new(symbol=order.symbol,
                                                       orderQty=order.order_qty,
                                                       price=order.price,
                                                       side=order.side,
                                                       text=order.text,
                                                       ordType=order.order_type).result()[0])
        logging.info(f"Submit Resp: {result}")
        return result

    def cancel_order(self, order_id):
        return dto.OrderResp(self.client.Order.Order_cancel(orderID=order_id).result()[0][0])

    def cancel_all(self):
        orders = self.client.Order.Order_cancelAll().result()[0]
        orders_dto = []
        for order in orders:
            orders_dto.append(dto.OrderResp(order))

        return orders_dto

    def submit_leverage(self, leverage):
        # Send 0 to enable cross margin.
        result = self.client.Position.Position_updateLeverage(
            symbol="XBTUSD",
            leverage=leverage).result()

        return result

    def get_last_trades(self):
        return self.ws.recent_trades()

    def get_funds(self):
        return self.ws.funds()

    def get_available_balance(self):
        return self.get_funds()["availableMargin"]

    def get_positions(self):
        return dto.PositionResp(self.ws.data['position'][0])

    def get_position_margin(self):
        return self.get_positions()[0]["maintMargin"]

    def get_open_order_margin(self):
        return self.get_positions()[0]["initMargin"]
