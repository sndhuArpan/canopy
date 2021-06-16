import telegram as tele

telegram_id_list = ['464308445', '506426930']
token = '564398612:AAEXUIfrJVFHfBnxS4Uot0Ob5vDPN8Ws69I'
bot = tele.Bot(token=token)


class telegram:

    @staticmethod
    def send_text(message):
        for telegram_id in telegram_id_list:
            bot.sendMessage(telegram_id, message)

    @staticmethod
    def send_file(file):
        for telegram_id in telegram_id_list:
            bot.sendDocument(telegram_id, file)

