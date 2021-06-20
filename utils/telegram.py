import telegram as tele
import os, pathlib, datetime

from Logging.Logger import GetLogger

telegram_id_list = ['464308445', '506426930']
token = '564398612:AAEXUIfrJVFHfBnxS4Uot0Ob5vDPN8Ws69I'
bot = tele.Bot(token=token)


class telegram:
    logger_dir = os.path.join(pathlib.Path.home(), 'Log/Telegram')
    date_str = datetime.datetime.now().strftime("%d%m%Y")
    log_file_name = 'market_data_' + date_str + '.log'
    log_file = os.path.join(logger_dir, log_file_name)
    logger = GetLogger(log_file).get_logger()

    @staticmethod
    def send_text(message):
        try:
            for telegram_id in telegram_id_list:
                telegram.logger.info(f'Sending message to telegram_id: {telegram_id}')
                bot.sendMessage(telegram_id, message)
        except Exception as e:
            telegram.logger.error('Exception occurred while generating send telegram message {error}'.format(error=str(e)))

    @staticmethod
    def send_file(csv_file_path):
        try:
            for telegram_id in telegram_id_list:
                telegram.logger.info(f'Sending csv to telegram_id: {telegram_id}')
                csv_file = open(csv_file_path, 'rb')
                bot.sendDocument(telegram_id, document=csv_file)
        except Exception as e:
            telegram.logger.error('Exception occurred while generating send file via telegram {error}'.format(error=str(e)))

