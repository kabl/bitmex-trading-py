import logging
import json
import bitmex
#from bitmex_websocket import BitMEXWebsocket
import dto
import utils


class Client:
    def __init__(self, api_key, api_secret, main_net=False):
        logging.info(f"Initialize client. Main net: {main_net}")
        if main_net:
            self.client = bitmex.bitmex(test=False, api_key=api_key, api_secret=api_secret)
            # self.ws = BitMEXWebsocket(endpoint="https://www.bitmex.com/api/v2", symbol="XBTUSD", api_key=api_key,
            #                          api_secret=api_secret)
        else:
            self.client = bitmex.bitmex(test=True, api_key=api_key, api_secret=api_secret)
            # self.ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v2", symbol="XBTUSD", api_key=api_key,
            #                          api_secret=api_secret)

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

    def buy_market(self, quantity):
        logging.info(f"Submit_market order quantity: {quantity}")

        result = dto.OrderResp(self.client.Order.Order_new(symbol="XBTUSD",
                                                       orderQty=quantity,
                                                       side=str(dto.Side.BUY),
                                                       text="Buy market",
                                                       ordType="Market").result()[0])
        logging.info(f"Submit Resp: {result}")
        return result

    def cancel_order(self, order_id):
        return dto.OrderResp(self.client.Order.Order_cancel(orderID=order_id).result()[0][0])

    def cancel_all_orders(self):
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

    def sell_position_at_market(self):
        logging.info("Sell whole position at market")
        result = self.client.Order.Order_closePosition(symbol='XBTUSD').result()
        logging.info(f"Sell Resp: {result}")

    def get_wallet(self):
        result = self.client.User.User_getMargin().result()
        return dto.WalletResp(result[0])

    def get_positions(self):
        pos_filter = json.dumps({"symbol": "XBTUSD"})
        result = self.client.Position.Position_get(filter=pos_filter).result()
        logging.info(f"[P] {result}")
        return dto.PositionResp(result[0][0])

    def get_price(self):
        inst_filter = json.dumps({"symbol": "XBTUSD"})
        result = self.client.Instrument.Instrument_get(filter=inst_filter).result()
        return dto.PriceResp(result[0][0])


    #def get_price(self):
    #    return dto.PriceResp(self.ws.get_instrument())

    # def get_wallet(self):
    #    return dto.WalletResp(self.ws.funds())

    # def get_positions(self):
    #    return dto.PositionResp(self.ws.data['position'][0])

    # not used
    # def get_last_trades(self):
    #    return self.ws.recent_trades()