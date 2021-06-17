import logging
import threading
import time

from src.DB.canopy.canopy_db import canopy_db
from src.strategies.CurrencyStrategy import CurrencyStrategy
from src.strategies.CurrencyStrategy_30 import CurrencyStrategy_30
from src.strategies.SampleStrategy import SampleStrategy
from src.DB.static_db.TickerDetails import TickerDetails


class Algo:

    @staticmethod
    def startAlgo():
        # if Utils.isMarketClosedForTheDay():
        #     logging.warning("%s: Not going to run strategy as market is closed.", self.getName())
        #     return
        #
        TickerDetails().load_data_into_symbol_token_map()
        logging.info("Starting Algo...")

        all_strategies_job = []
        all_strategies_name = []
        # start running strategies: Run each strategy in a separate thread
        # threading.Thread(target=SampleStrategy.getInstance().run).start()
        # threading.Thread(target=BNFORB30Min.getInstance().run).start()
        all_strategies_job.append(threading.Thread(target=CurrencyStrategy_30.getInstance().run))
        all_strategies_name.append('CurrencyStrategy_30')
        # threading.Thread(target=TradeManager.update_trade_status).start()

        for job in all_strategies_job:
            job.start()
        for job in all_strategies_job:
            job.join()

        ### create daily csv and deleting all daily data
        canopy_sql = canopy_db()
        for strategy_name in all_strategies_name:
            canopy_sql.create_csv(strategy_name=strategy_name, delete=True)

        logging.info("Algo started.")
