import telegram
import telebot
import requests
import time
import datetime
import proj_constant_var as const

telegram_id_list = ['464308445','506426930']
send_pdf_token = '564398612:AAEXUIfrJVFHfBnxS4Uot0Ob5vDPN8Ws69I'

def sendTextTelegram(totalResponse, chatId):
    try:
        #print("in sendTelegram", totalResponse)
        bot_id = "bot564398612:AAEXUIfrJVFHfBnxS4Uot0Ob5vDPN8Ws69I"
        url = "https://api.telegram.org/" + bot_id + "/sendMessage?chat_id=" + str(chatId) + "&text= " + str(totalResponse)
        requests.get(url)
        return True
    except Exception as e:
        print(e)
        time.sleep(30)
        sendTextTelegram(totalResponse, chatId)

def send_text_to_telegram(findings):
    print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') +" : Sending Text to telegram Started"
    for id in const.telegram_id_list:
        for record in findings:
            sendTextTelegram(record,id)
    print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') +" : Sending Text to telegram Finished"


def send_pdf_to_user(pdf_file):
    for id in const.telegram_id_list:
        token = const.send_pdf_token
        tb = telebot.TeleBot(token)
        document = open(pdf_file,'rb')
        tb.send_document(id,document)
        print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " : File Sent to Telegram on " +