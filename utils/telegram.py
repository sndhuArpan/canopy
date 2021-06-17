import telegram as tele
import logging

telegram_id_list = ['464308445', '506426930']
token = '564398612:AAEXUIfrJVFHfBnxS4Uot0Ob5vDPN8Ws69I'
bot = tele.Bot(token=token)


class telegram:

    @staticmethod
    def send_text(message):
        try:
            for telegram_id in telegram_id_list:
                bot.sendMessage(telegram_id, message)
        except Exception as e:
            logging.error('Exception occurred while generating send telegram message {error}'.format(error=str(e)))

    @staticmethod
    def send_file(csv_file_path):
        try:
            for telegram_id in telegram_id_list:
                csv_file = open(csv_file_path, 'rb')
                bot.sendDocument(telegram_id, document=csv_file)
        except Exception as e:
            logging.error('Exception occurred while generating send file via telegram {error}'.format(error=str(e)))

