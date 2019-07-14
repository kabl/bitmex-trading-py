import json
from enum import Enum
from Utils import *


class OrderResp:
    def __init__(self, order_dict):
        self.symbol = order_dict["symbol"]
        self.side = order_dict["side"]
        self.order_qty = order_dict["orderQty"]
        self.price = order_dict["price"]
        self.order_type = order_dict["ordType"]
        self.order_status = order_dict["ordStatus"]
        self.order_value = int(Calc.XBT_to_XBt(self.order_qty / self.price))
        self.text = order_dict["text"]
        self.order_id = order_dict["orderID"]

    def __repr__(self):
        return json.dumps(self.__dict__)


class Side(Enum):
    BUY = "Buy",
    SELL = "Sell",

    def __str__(self):
        return str(self.value[0])


class LimitOrderReq:
    def __init__(self, side: Side, order_qty, price_XBTUSD, text):
        self.side = str(side)
        self.order_qty = order_qty
        self.price = price_XBTUSD
        self.order_value_XBt = Calc.XBT_to_XBt(order_qty / price_XBTUSD)
        self.text = text
        self.symbol = "XBTUSD"
        self.order_type = "Limit"

    def __repr__(self):
        return json.dumps(self.__dict__)

    @classmethod
    def create(cls, side: Side, price_XBTUSD, available_balance_XBt, invest_percentage, text):
        invest_balance = int(available_balance_XBt * (invest_percentage / 100))

        price_XBTUSD = Calc.round_price(price_XBTUSD)

        if(invest_balance < Calc.spam_protection_invest_XBt): #Spam protection
            print("invest balance too small. Spam protection. Use more than: {}%".format(invest_percentage))
            invest_balance = Calc.spam_protection_invest_XBt

        quantity = Calc.round_quantity(price_XBTUSD * Calc.XBt_to_XBT(invest_balance))
        order = LimitOrderReq(side, quantity, price_XBTUSD, text)

        if(order.order_value_XBt > available_balance_XBt):
            raise NotEnoughBalanceException()

        if(order.order_value_XBt < Calc.spam_protection_invest_XBt):
            raise SpamProtectionException()

        return order

    @classmethod
    def create_sell_higher(cls, prev_order, sell_price_XBTUSD):

        sell_price_XBTUSD = Calc.round_price(sell_price_XBTUSD)
        adjusted_quantity = prev_order.order_qty * (sell_price_XBTUSD / prev_order.price)
        adjusted_quantity = Calc.round_quantity(adjusted_quantity)

        order = LimitOrderReq(Side.SELL, adjusted_quantity, sell_price_XBTUSD, "profit_order: " + prev_order.order_id)

        # TODO: Validate enough liquidity

        if order.order_value_XBt < Calc.spam_protection_invest_XBt:
            raise SpamProtectionException()

        return order

    @classmethod
    def create_buy_lower(cls, prev_order, buy_price_XBTUSD):

        buy_price_XBTUSD = Calc.round_price(buy_price_XBTUSD)
        quantity = int(prev_order.order_qty)

        order = LimitOrderReq(Side.BUY, quantity, buy_price_XBTUSD, "profit_order: " + prev_order.order_id)

        # TODO: Validate enough liquidity

        if order.order_value_XBt < Calc.spam_protection_invest_XBt:
            raise SpamProtectionException()

        return order


class PositionResp:
    def __init__(self, position_dict):
        self.current_qty = position_dict["currentQty"]
        self.leverage = position_dict["leverage"]
        self.liquidation_price = position_dict["liquidationPrice"]
        self.mark_price = position_dict["markPrice"]
        self.open_order_margin = position_dict["initMargin"]
        self.position_margin = position_dict["maintMargin"]

    def __repr__(self):
        return json.dumps(self.__dict__)