import configparser
import json


class Config:
    def __init__(self, file_name="config-test.ini"):
        config = configparser.ConfigParser()
        config.read(file_name)

        self.api_key = config["CREDENTIALS"]["API_KEY"]
        self.api_secret = config["CREDENTIALS"]["API_SECRET"]
        self.main_net = config.getboolean("CREDENTIALS", "MAIN_NET")

        self.order_size_pc = config.getfloat("INVEST_RULES", "ORDER_SIZE")
        self.band_pc = config.getfloat("INVEST_RULES", "BAND")
        self.take_profit_pc = config.getfloat("INVEST_RULES", "TAKE_PROFIT")
        self.leverage = config.getfloat("INVEST_RULES", "LEVERAGE")

        self.check_interval = config.getint("DEFAULT", "CHECK_INTERVAL")
        self.log_to_file = config.getboolean("DEFAULT", "LOG_TO_FILE")

    def __repr__(self):
        return json.dumps(self.__dict__)
