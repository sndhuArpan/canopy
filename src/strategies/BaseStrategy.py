import logging
import time
from datetime import datetime

from Data_Wrappers.Angel_Broker.Angel_Broker_Wrapper import Angel_Broker_Wrapper
from src.models.Exchange import Exchange
from src.models.ProductType import ProductType
from utils.Utils import Utils


class BaseStrategy:
    def __init__(self, name):
        # NOTE: All the below properties should be set by the Derived Class (Specific to each strategy)
        self.name = name  # strategy name
        self.productType = ProductType.MIS  # MIS/NRML/CNC etc
        self.symbols = []  # List of stocks to be traded under this strategy
        self.slPercentage = 0
        self.exchange = Exchange.NSE
        self.startTimestamp = Utils.getMarketStartTime()  # When to start the strategy. Default is Market start time
        self.stopTimestamp = None  # This is not square off timestamp. This is the timestamp after which no new trades will be placed under this strategy but existing trades continue to be active.
        self.squareOffTimestamp = None  # Square off time
        self.tradesCreatedSymbols = []  # Add symbol to this list when a trade is created
        self.angel_data = Angel_Broker_Wrapper()
        self.max_buy_call = 1
        self.max_sl_call = 1
        self.max_sell_call = 1
        self.incubation = True  # Strategy will be run only when it is enabled
        # Register strategy with trade manager
        # TradeManager.registerStrategy(self)

    def getName(self):
        return self.name

    def isEnabled(self):
        return self.enabled

    def setDisabled(self):
        self.enabled = False

    def process(self):
        # Implementation is specific to each strategy - To defined in derived class
        logging.info("BaseStrategy process is called.")
        pass

    def calculateCapitalPerTrade(self):
        capitalPerTrade = int(self.capital * self.leverage / self.maxTradesPerDay)
        return capitalPerTrade

    def canTradeToday(self):
        # Derived class should override the logic if the strategy to be traded only on specific days of the week
        return True

    def run(self):
        now = datetime.now()
        if now < self.startTimestamp:
            waitSeconds = Utils.getEpoch(self.startTimestamp) - Utils.getEpoch(now)
            logging.info("%s: Waiting for %d seconds till startegy start timestamp reaches...", self.getName(),
                         waitSeconds)
            if waitSeconds > 0:
                time.sleep(waitSeconds)

        self.process()

    def placeTrade(self, trade):
        pass
