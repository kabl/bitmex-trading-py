import unittest
from dto import LimitOrderReq
from types import SimpleNamespace


class LimitOrderReqTest(unittest.TestCase):

    def test_create_sell_higher(self):
        prev_order = SimpleNamespace()
        prev_order.order_qty = 25
        prev_order.price = 9000
        prev_order.order_id = "test"
        order = LimitOrderReq.create_sell_higher(prev_order, 10000)
        self.assertEqual(order.order_qty, 28)

    def test_create_buy_lower(self):
        prev_order = SimpleNamespace()
        prev_order.order_qty = 25
        prev_order.price = 10000
        prev_order.order_id = "test"
        order = LimitOrderReq.create_buy_lower(prev_order, 9000)
        self.assertEqual(order.order_qty, 25)


if __name__ == '__main__':
    unittest.main()