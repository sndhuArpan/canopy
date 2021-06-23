from datetime import datetime

import pandas as pd

from flask import Flask, request, render_template, jsonify, url_for, redirect
import os
import pathlib
import json

from src.DB.canopy.canopy_db import canopy_db
from src.DB.market_data.Market_Data import MarketData
from src.DB.static_db.static_db import static_db

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/Alert')
def Alert():
    return render_template('alertPage.html')


@app.route('/DB')
def DB():
    dbs = ["canopy", "market_data", "static_db"]
    return render_template('dbPage.html', dbs=dbs)


@app.route('/Log')
def Log():
    get_file_dir = os.path.dirname(__file__)
    comp_path = os.path.join(get_file_dir, '../Log/')
    folders = os.listdir(comp_path)
    all_files = []
    date_str = '18062021'#datetime.now().strftime("%d%m%Y")
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
    get_file_dir = os.path.dirname(__file__)
    comp_path = os.path.join(get_file_dir, '../Log/')
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

    return jsonify(table_df.to_html())

if __name__ == '__main__':
    app.run(debug=True)
