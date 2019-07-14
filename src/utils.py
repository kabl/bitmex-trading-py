import math


class NotEnoughBalanceException(Exception):
    """Raised when the input value is too small"""
    pass


class SpamProtectionException(Exception):
    pass


class Calc:
    spam_protection_invest_XBt = 250000

    @classmethod
    def round_price(cls, price):
        # rounding to x.0 or x.5
        return round(price * 2) / 2

    @classmethod
    def round_quantity(cls, quantity):
        return int(math.ceil(quantity))

    @classmethod
    def XBT_to_XBt(cls, XBT):
        return XBT * 100000000

    @classmethod
    def XBt_to_XBT(cls, XBt):
        return XBt / 100000000
