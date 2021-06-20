import datetime
import os
import pathlib
import sys
import traceback

sys.path.append('/home/ec2-user/canopy/canopy')
sys.path.append('/Users/Sandhu/canopy/canopy/')
sys.path.append('/Users/Sandhu/canopy/canopy/src')
sys.path.append('/Users/arpanjeetsandhu/canopy/')
sys.path.append('/Users/arpanjeetsandhu/canopy/src')

from Logging.Logger import GetLogger
from src.DB.market_data.MarketDataWebSocket import MarketDataWebsocket


if __name__ == '__main__':
    logger_dir = os.path.join(pathlib.Path.home(), 'Log/MarketData')
    date_str = datetime.datetime.now().strftime("%d%m%Y")
    log_file_name = 'market_data_' + date_str + '.log'
    log_file = os.path.join(logger_dir, log_file_name)
    logger = GetLogger(log_file).get_logger()
    logger.info('Starting Logger for first time today')
    logger.info('#####    START  ####')
    logger.info('Creating Websocket object')
    market_data_obj = MarketDataWebsocket('S705342', logger)
    try:
        logger.info('Initiating start_ticker')
        market_data_obj.start_ticker()
        del market_data_obj
    except Exception as e:
        logger.error('Exception : {0}\n{1}'.format(str(e), traceback.format_exc()))
        logger.error('#####   TICKER STOPPED   ####')
        logger.info('Deleting existing Obj')
        del market_data_obj
