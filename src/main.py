import time
import logging
import bravado
import traderconfig
import traderbot
import bitmexclient
import utils


def main():
    config = traderconfig.Config("./config.ini")
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
    client = bitmexclient.Client(config.api_key, config.api_secret)
    client.submit_leverage(config.leverage)

    bot = traderbot.Bot(client, config)
    bot.init_bands()
    run_bot(bot, client, config.check_interval)


def run_bot(bot, client, check_interval):
    while True:
        try:
            bot.check_and_update()
            logging.info("[-] INFOS")
            logging.info(f"[P] {client.get_positions()}")
            logging.info(f"[$] {client.get_last_price()}")
            for order in client.get_orders():
                logging.info(f"[O] {order}")

            time.sleep(check_interval)
        except utils.NotEnoughBalanceException:
            logging.warning("Not enough balance in the wallet!", exc_info=True)
            time.sleep(check_interval)
        except bravado.exception.HTTPBadRequest:
            logging.warning("HTTPBadRequest", exc_info=True)
            time.sleep(check_interval)


if __name__ == '__main__':
    main()
