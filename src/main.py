import time
import logging
import sys
import bravado
import traderconfig
import traderbot
import bitmexclient
import utils


def main():
    if len(sys.argv) != 2:
        print("Config file missing")
        print(f"{sys.argv[0]} <CONFIG FILE>")
        exit(0)

    # config = traderconfig.Config("./config-test.ini")
    config = traderconfig.Config(sys.argv[1])
    print("Configuration:", config)
    if config.log_to_file:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%d-%b-%y %H:%M:%S',
                            filename='./app.log',
                            filemode='w')
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%d-%b-%y %H:%M:%S')

    logging.info("Hello Bitmex Trading Bot. Logger")
    logging.info(f"Config: {config}")
    client = bitmexclient.Client(config.api_key, config.api_secret, config.main_net)
    client.submit_leverage(config.leverage)

    # while True:
    #    print(client.get_price())
    #    time.sleep(5)

    wallet = client.get_wallet()
    position = client.get_positions()
    price = client.get_price()

    logging.info(f"[W] {wallet}")
    logging.info(f"[P] {position}")
    logging.info(f"[$] {price}")

    if position.current_qty == 0:
        logging.info(f"[+] No quantity available. Init with 50%. {position}")
        quantity = utils.Calc.round_quantity(price.last_price * utils.Calc.XBt_to_XBT(wallet.available_balance / 2))
        print("Quantity: " + str(quantity))
        client.buy_market(quantity)
    else:
        logging.info("[-] Bot was initialized before. Start with the bands")

    #client.sell_position_at_market()
    bot = traderbot.Bot(client, config)
    bot.init_bands()
    run_bot(bot, client, config.check_interval)


def run_bot(bot, client, check_interval):
    while True:
        try:
            bot.check_and_update()
            logging.info("[-] INFOS")
            logging.info(f"[W] {client.get_wallet()}")
            logging.info(f"[P] {client.get_positions()}")
            logging.info(f"[$] {client.get_price()}")

            for order in client.get_orders():
                logging.info(f"[O] {order}")

            time.sleep(check_interval)
        except utils.NotEnoughBalanceException:
            logging.warning("Not enough balance in the wallet!", exc_info=True)
            time.sleep(check_interval)
        except bravado.exception.HTTPBadRequest:
            logging.warning("HTTPBadRequest", exc_info=True)
            time.sleep(check_interval)
        except Exception:
            logging.warning("Exception", exc_info=True)
            time.sleep(check_interval)


if __name__ == '__main__':
    main()
