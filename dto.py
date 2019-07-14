import json
from enum import Enum
from Utils import *


class OrderResp:
    def __init__(self, order_dict):
        self.order_id = order_dict["orderID"]
        self.symbol = order_dict["symbol"]
        self.side = order_dict["side"]
        self.order_qty = order_dict["orderQty"]
        self.price = order_dict["price"]
        self.order_type = order_dict["ordType"]
        self.order_status = order_dict["ordStatus"]
        self.text = order_dict["text"]

    def __repr__(self):
        return json.dumps(self.__dict__)


class Side(Enum):
    BUY = "Buy",
    SELL = "Sell",

    def __str__(self):
        return str(self.value[0])


class LimitOrderReq:
    def __init__(self, side: Side, quantity, price_XBTUSD, text):
        self.side = str(side)
        self.quantity = quantity
        self.price = price_XBTUSD
        self.order_value_XBt = Calc.XBT_to_XBt(quantity / price_XBTUSD)
        self.text = text
        self.symbol = "XBTUSD"
        self.order_type = "Limit"

    def __repr__(self):
        return json.dumps(self.__dict__)

    @classmethod
    def create(cls, side: Side, price_XBTUSD, available_balance_XBt, invest_percentage, text):
        invest_balance = int(available_balance_XBt * invest_percentage)

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
    def create2(cls, side: Side, price_XBTUSD, quantity, text):
        price_XBTUSD = Calc.round_price(price_XBTUSD)
        quantity = int(quantity)

        # TODO: Spam protection
        order = LimitOrderReq(side, quantity, price_XBTUSD, text)

        # TODO: Validate enough liquidity

        if(order.order_value_XBt < Calc.spam_protection_invest_XBt):
            raise SpamProtectionException()

        return order


class PositionResp:
    def __init__(self, position_dict):
        self.quantity = position_dict["currentQty"]
        self.leverage = position_dict["leverage"]
        self.liquidation_price = position_dict["liquidationPrice"]
        self.mark_price = position_dict["markPrice"]
        self.open_order_margin = position_dict["initMargin"]
        self.position_margin = position_dict["maintMargin"]

    def __repr__(self):
        return json.dumps(self.__dict__)