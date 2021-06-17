import logging
import threading
import time

from src.strategies.CurrencyStrategy import CurrencyStrategy
from src.strategies.CurrencyStrategy_30 import CurrencyStrategy_30
from src.strategies.SampleStrategy import SampleStrategy
from src.DB.static_db.TickerDetails import TickerDetails

# from Test import Test
from src.trademanager.TradeManager import TradeManager


class Algo:
    isAlgoRunning = None

    def __init__(self):
        #SYMBOL load each day
        TickerDetails().load_data_into_symbol_token_map()


    @staticmethod
    def startAlgo():
        if Algo.isAlgoRunning == True:
            logging.info("Algo has already started..")
            return
        TickerDetails().load_data_into_symbol_token_map()
        logging.info("Starting Algo...")

        # start trade manager in a separate thread


        # sleep for 2 seconds for TradeManager to get initialized
        time.sleep(2)

        # start running strategies: Run each strategy in a separate thread
        # threading.Thread(target=SampleStrategy.getInstance().run).start()
        # threading.Thread(target=BNFORB30Min.getInstance().run).start()
        threading.Thread(target=CurrencyStrategy_30.getInstance().run).start()
        # threading.Thread(target=TradeManager.update_trade_status).start()

        Algo.isAlgoRunning = True
        logging.info("Algo started.")
