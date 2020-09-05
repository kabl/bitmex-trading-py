import logging
import json
from enum import Enum
import utils


class OrderResp:
    def __init__(self, order_dict):
        self.symbol = order_dict["symbol"]
        self.side = order_dict["side"]
        self.order_qty = order_dict["orderQty"]
        self.price = order_dict["price"]
        self.order_type = order_dict["ordType"]
        self.order_status = order_dict["ordStatus"]
        self.order_value = int(utils.Calc.XBT_to_XBt(self.order_qty / self.price))
        self.text = order_dict["text"]
        self.order_id = order_dict["orderID"]

    def __repr__(self):
        return json.dumps(self.__dict__)


class Side(Enum):
    BUY = "Buy"
    SELL = "Sell"

    def __str__(self):
        return str(self.value)


class LimitOrderReq:
    def __init__(self, side: Side, order_qty, price_XBTUSD, text):
        self.side = str(side)
        self.order_qty = order_qty
        self.price = price_XBTUSD
        self.order_value_XBt = utils.Calc.XBT_to_XBt(order_qty / price_XBTUSD)
        self.text = text
        self.symbol = "XBTUSD"
        self.order_type = "Limit"

    def __repr__(self):
        return json.dumps(self.__dict__)

    @classmethod
    def create(cls, side: Side, price_XBTUSD, available_balance_XBt, invest_percentage, text, spam_protection=True):
        invest_balance = int(available_balance_XBt * (invest_percentage / 100))

        price_XBTUSD = utils.Calc.round_price(price_XBTUSD)

        if invest_balance < utils.Calc.spam_protection_invest_XBt:  # Spam protection
            logging.warning(f"Spam protection. Set to minimum value: {utils.Calc.spam_protection_invest_XBt}")
            invest_balance = utils.Calc.spam_protection_invest_XBt

        quantity = utils.Calc.round_quantity(price_XBTUSD * utils.Calc.XBt_to_XBT(invest_balance))
        order = LimitOrderReq(side, quantity, price_XBTUSD, text)

        if order.order_value_XBt > available_balance_XBt:
            raise utils.NotEnoughBalanceException()

        if spam_protection:
            if order.order_value_XBt < utils.Calc.spam_protection_invest_XBt:
                raise utils.SpamProtectionException()

        return order

    @classmethod
    def create_sell_higher(cls, prev_order, sell_price_XBTUSD):

        sell_price_XBTUSD = utils.Calc.round_price(sell_price_XBTUSD)
        adjusted_quantity = prev_order.order_qty * (sell_price_XBTUSD / prev_order.price)
        adjusted_quantity = utils.Calc.round_quantity(adjusted_quantity)

        order = LimitOrderReq(Side.SELL,
                              adjusted_quantity,
                              sell_price_XBTUSD,
                              "profit_order: " + prev_order.order_id)

        # TODO: Validate enough liquidity

        if order.order_value_XBt < utils.Calc.spam_protection_invest_XBt:
            raise utils.SpamProtectionException()

        return order

    @classmethod
    def create_buy_lower(cls, prev_order, buy_price_XBTUSD):

        buy_price_XBTUSD = utils.Calc.round_price(buy_price_XBTUSD)
        quantity = int(prev_order.order_qty)

        order = LimitOrderReq(Side.BUY,
                              quantity,
                              buy_price_XBTUSD,
                              "profit_order: " + prev_order.order_id)

        # TODO: Validate enough liquidity

        if order.order_value_XBt < utils.Calc.spam_protection_invest_XBt:
            raise utils.SpamProtectionException()

        return order


class PositionResp:
    def __init__(self, position_dict):
        self.current_qty = position_dict["currentQty"]
        self.leverage = position_dict["leverage"]
        self.liquidation_price = position_dict["liquidationPrice"]
        # self.mark_price = position_dict["markPrice"]
        # self.order_margin = position_dict["initMargin"]
        # self.position_margin = position_dict["maintMargin"]

    def __repr__(self):
        return json.dumps(self.__dict__)


class WalletResp:
    def __init__(self, funds_dict):
        self.wallet_balance = funds_dict["walletBalance"]
        self.available_balance = funds_dict["availableMargin"]
        self.unrealised_pnl = funds_dict["unrealisedPnl"]
        # self.margin_balance = funds_dict["marginBalance"] # wallet_balance + unrealised_pnl
        self.order_margin = funds_dict["initMargin"]
        self.position_margin = funds_dict["maintMargin"]

    def __repr__(self):
        return json.dumps(self.__dict__)


class PriceResp:
    def __init__(self, price_dict):
        # self.fair_price = price_dict["fairPrice"]
        self.mark_price = price_dict["markPrice"]
        self.last_price = price_dict["lastPrice"]
        self.low_price = price_dict["lowPrice"]
        self.high_price = price_dict["highPrice"]
        self.prev_24h = price_dict["prevPrice24h"]

    def __repr__(self):
        return json.dumps(self.__dict__)