import threading
from datetime import datetime
import os
import pathlib

from Logging.Logger import GetLogger
from src.DB.canopy.canopy_db import canopy_db
from src.strategies.CurrencyStrategy_30 import CurrencyStrategy_30
from src.DB.static_db.TickerDetails import TickerDetails
from utils.Utils import Utils


class Algo:

    @staticmethod
    def startAlgo():

        # Creating Logging
        logger_dir = os.path.join(pathlib.Path.home(), 'Log/Algo')
        date_str = datetime.now().strftime("%d%m%Y")
        log_file_name = 'Algo_' + date_str + '.log'
        log_file = os.path.join(logger_dir, log_file_name)
        logger = GetLogger(log_file).get_logger()

        if Utils.isMarketClosedForTheDay():
            logger.info("Not going to run strategy as market is closed.")
            return

        TickerDetails().load_data_into_symbol_token_map()
        logger.info("Starting Algo...")

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

        logger.info("Algo started.")

if __name__ == '__main__':
    Algo.startAlgo()
