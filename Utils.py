import math


class NotEnoughBalanceException(Exception):
   """Raised when the input value is too small"""
   pass


class SpamProtectionException(Exception):
    pass


class Calc:
    spam_protection_invest_XBt = 250000

    def round_price(price):
        return round(price * 2) / 2 #rounding to x.0 or x.5

    def round_quantity(quantity):
        return int(math.ceil(quantity))

    def XBT_to_XBt(XBT):
        return XBT * 100000000

    def XBt_to_XBT(XBt):
        return XBt / 100000000

    def calc_invest_quantity_old(price_XBTUSD, available_balance_XBt, invest_percentage):
        invest_balance = int(available_balance_XBt * invest_percentage)

        if(invest_balance < Calc.spam_protection_invest_XBt): #Spam protection
            print("invest balance too small. Spam protection. Use more than: {}%".format(invest_percentage))
            invest_balance = Calc.spam_protection_invest_XBt

        quantity = Calc.round_quantity(price_XBTUSD * Calc.XBt_to_XBT(invest_balance))
        order_value_XBt = Calc.XBT_to_XBt(quantity / price_XBTUSD)

        if(order_value_XBt > available_balance_XBt):
            raise NotEnoughBalanceException()

        if(order_value_XBt < Calc.spam_protection_invest_XBt):
            raise SpamProtectionException()

        print("Quantity: {} $ equals: {} XBt, total balance: {} XBt, price: {} USD".format(quantity, invest_balance, available_balance_XBt, price_XBTUSD))
        return quantity

