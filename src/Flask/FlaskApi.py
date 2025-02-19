import sys

from src.DB.postional.positional_db import positional_db, positional_model, trade_status
from src.DB.static_db.BrokerAppDetails import BrokerAppDetails
from src.DB.static_db.ClientStrategyInfo import ClientStrategyInfo

sys.path.append('/home/ec2-user/canopy/canopy')
sys.path.append('/Users/Sandhu/canopy/canopy/')
sys.path.append('/Users/Sandhu/canopy/canopy/src')
sys.path.append('/Users/arpanjeetsandhu/canopy/')
sys.path.append('/Users/arpanjeetsandhu/canopy/src')

from datetime import datetime

import pandas as pd

from flask import Flask, request, render_template, jsonify, url_for, redirect
import os
import pathlib
import json

from src.DB.canopy.canopy_db import canopy_db
from src.DB.market_data.Market_Data import MarketData
from src.DB.static_db.TickerDetails import TickerDetails
from src.DB.static_db.alert_trigger import alert_trigger, alert_trigger_model
from src.DB.static_db.static_db import static_db
from src.core.alert_checker import alert_checker
from utils.Utils import Utils, interval_enum

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/Alert')
def Alert():
    ticker_sql = TickerDetails()
    all_stocks = ticker_sql.get_all_stocks('nse')
    valid_stocks = []
    for stock in all_stocks:
        if '-EQ' in stock.symbol:
            valid_stocks.append(stock.symbol)
    all_interval = []
    for interval in interval_enum:
        if interval.name in alert_checker.valid_interval:
            all_interval.append(interval.name)
    return render_template('alertPage.html', valid_stocks=valid_stocks, all_interval=all_interval)


@app.route('/add_trade')
def add_trade():
    ticker_sql = TickerDetails()
    all_stocks = ticker_sql.get_all_stocks('nse')
    valid_stocks = []
    for stock in all_stocks:
        if '-EQ' in stock.symbol:
            valid_stocks.append(stock.symbol)
    all_interval = []
    for interval in interval_enum:
        if interval.name in alert_checker.valid_interval:
            all_interval.append(interval.name)
    return render_template('addTradePage.html', valid_stocks=valid_stocks, all_interval=all_interval)


@app.route('/add_stock', methods=['POST'])
def add_stock():
    selected_stock = request.form['selected_stock']
    price = request.form['price']
    db = positional_db()
    client_list = ClientStrategyInfo().get_client_by_strategy('Positional')
    for client in client_list:
        model = positional_model(symbol=selected_stock, entry_price=price, client_id=client)
        db.insert_trade(model)
    return get_all_added_stock_json(db)


@app.route('/delete_stock', methods=['POST'])
def delete_stock():
    id = request.form['id']
    db = positional_db()
    db.delete_trade(int(id))
    return get_all_added_stock_json(db)


@app.route('/update_stock', methods=['POST'])
def update_stock():
    id = request.form['id']
    entry_price = request.form['entry_price']

    db = positional_db()
    db.update_trade_price(int(id), float(entry_price))
    return get_all_added_stock_json(db)


@app.route('/see_added_stocks', methods=['GET'])
def see_added_stocks():
    db = positional_db()
    return get_all_added_stock_json(db)


def get_all_added_stock_json(db):
    all_added_stocks = db.get_trade_by_status(status_list=[trade_status.CREATED.name])
    return jsonify([stocks.to_dict() for stocks in all_added_stocks])


@app.route('/trades')
def trades():
    broker_db = BrokerAppDetails()
    client_list = broker_db.get_all_clients()
    return render_template('tradePage.html', client_list=client_list)


@app.route('/get_trades_client', methods=['POST'])
def get_trades_client():
    selected_client = request.form['selected_client']
    db = positional_db()
    all_trades = db.get_trade_by_client_status(client_id=selected_client, status_list=[trade_status.ACTIVE.name,
                                                                                       trade_status.HALF_BOOK.name])
    return jsonify([trade.to_dict() for trade in all_trades])


@app.route('/update_trade', methods=['POST'])
def update_trade():
    id = request.form['id']
    half_book_price = request.form['half_book_price']
    stoploss = request.form['stoploss']
    db = positional_db()
    db.update_trade_target_stoploss(int(id), half_book_price=float(half_book_price), stoploss=float(stoploss))
    trade = db.get_trade_by_id(int(id))
    all_trades = db.get_trade_by_client_status(client_id=trade.client_id, status_list=[trade_status.ACTIVE.name,
                                                                                       trade_status.HALF_BOOK.name])
    return jsonify([trade.to_dict() for trade in all_trades])


@app.route('/DB')
def DB():
    dbs = ["canopy", "market_data", "static_db", "positional_db"]
    return render_template('dbPage.html', dbs=dbs)


@app.route('/Log')
def Log():
    comp_path = os.path.join(pathlib.Path.home(), 'Log/')
    folders = os.listdir(comp_path)
    all_files = []
    date_str = datetime.now().strftime("%d%m%Y")
    for i in folders:
        files = os.listdir(comp_path + "/" + i)
        for f in files:
            if date_str in f:
                all_files.append(f)
                break
    return render_template('logPage.html', log_files=all_files)


@app.route('/selected_log', methods=['GET'])
def get_log_file_val():
    selected_log = request.args.get('selected_log')
    comp_path = os.path.join(pathlib.Path.home(), 'Log/')
    folders = os.listdir(comp_path)
    log_string = ""
    for i in folders:
        files = os.listdir(comp_path + "/" + i)
        for f in files:
            if selected_log == f:
                log_string = open(os.path.join(comp_path + "/" + i, selected_log), "r").read()
                break
    return log_string


@app.route('/select_db', methods=['GET'])
def get_tables():
    selected_db = request.args.get('selected_db')
    all_tables = []
    if selected_db == 'canopy':
        canopy_sql = canopy_db()
        all_tables = canopy_sql.select_all_tables()
    if selected_db == 'market_data':
        market_sql = MarketData()
        all_tables = market_sql.select_all_tables()
    if selected_db == 'static_db':
        static_sql = static_db()
        all_tables = static_sql.select_all_tables()
    if selected_db == 'positional_db':
        positional_sql = positional_db()
        all_tables = positional_sql.select_all_tables()
    return jsonify(all_tables)


@app.route('/fetch_table_data', methods=['GET'])
def fetch_table_data():
    selected_table = request.args.get('selected_table')
    selected_db = request.args.get('selected_db')
    table_df = pd.DataFrame()
    if selected_db == 'canopy':
        canopy_sql = canopy_db()
        table_df = canopy_sql.select_table_as_dataframe(selected_table)
    if selected_db == 'market_data':
        market_sql = MarketData()
        table_df = market_sql.select_table_as_dataframe(selected_table)
    if selected_db == 'static_db':
        static_sql = static_db()
        table_df = static_sql.select_table_as_dataframe(selected_table)
    if selected_db == 'positional_db':
        positional_sql = positional_db()
        table_df = positional_sql.select_table_as_dataframe(selected_table)

    return jsonify(table_df.to_html())


@app.route('/indexPage', methods=['POST'])
def my_form_post():
    page_selected = request.form['page_selected']
    return page_selected


@app.route('/save_alert', methods=['POST'])
def save_alert():
    selected_stock = request.form['selected_stock']
    selected_interval = request.form['selected_interval']
    price = request.form['price']
    db = alert_trigger()
    model = alert_trigger_model(symbol=selected_stock, price=price, interval=selected_interval, triggered=0)
    db.insert_alert(model)
    return "done"


if __name__ == '__main__':
    app.run(port=8000, debug=True)
