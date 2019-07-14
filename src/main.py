import time
import bravado
import traderconfig
import traderbot
import bitmexclient
import utils


def main():
    print("Hello Bitmex Trading Bot")
    config = traderconfig.Config("../config.ini")
    print("Config:", config)
    client = bitmexclient.Client(config.api_key, config.api_secret)
    client.submit_leverage(config.leverage)

    bot = traderbot.Bot(client, config)
    bot.init_bands()
    run_bot(bot, client, config.check_interval)


def run_bot(bot, client, check_interval):
    while True:
        try:
            bot.check_and_update()
            print("[-] INFOS")
            print("[P]", client.get_positions())
            print("[$]", client.get_last_price())
            for order in client.get_orders():
                print("[O]", order)

            time.sleep(check_interval)
        except utils.NotEnoughBalanceException:
            print("Not enough balance in the wallet! Cancel all orders")
            # bot.cancel_all_orders()
            time.sleep(check_interval)
        except bravado.exception.HTTPBadRequest as ex:
            print("HTTPBadRequest:", ex)
            time.sleep(check_interval)


if __name__ == '__main__':
    main()
