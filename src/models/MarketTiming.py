class MarketTiming:
    country = None

    def __init__(self, country):
        MarketTiming.country = country

    @staticmethod
    def get_market_start_time():
        return None

    @staticmethod
    def is_market_closed_for_the_day():
        return None

    @staticmethod
    def wait_till_market_opens(a):
        return



if __name__ == '__main__':
    MarketTiming('India').print_cn()