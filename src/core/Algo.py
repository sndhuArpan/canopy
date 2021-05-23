import logging
import threading
import time

from src.strategies.SampleStrategy import SampleStrategy
from src.ticker.AngelSymbol.AngelSymbol import AngelSymbol


# from Test import Test


class Algo:
    isAlgoRunning = None

    @staticmethod
    def startAlgo():
        if Algo.isAlgoRunning == True:
            logging.info("Algo has already started..")
            return

        logging.info("Starting Algo...")
        AngelSymbol.create_csv_by_segment()

        # start trade manager in a separate thread


        # sleep for 2 seconds for TradeManager to get initialized
        time.sleep(2)

        # start running strategies: Run each strategy in a separate thread
        threading.Thread(target=SampleStrategy.getInstance().run).start()
        # threading.Thread(target=BNFORB30Min.getInstance().run).start()

        Algo.isAlgoRunning = True
        logging.info("Algo started.")
