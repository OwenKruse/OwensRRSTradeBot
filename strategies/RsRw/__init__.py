import datetime

import jesse.indicators as ta
import numpy as np
import statsmodels.api as sm
from jesse.strategies import Strategy
from scipy.stats import pearsonr

# get 6:30 am today from datetime
start = datetime.datetime.combine(datetime.date.today(), datetime.time(6, 30))
RSRN = 0
PRN = 0
candle1 = None
candle2 = None
candle3 = None

lincandles = [None, None, None, None, None, None]
rolling_change = []
rolling_RRSW = []

echange = None
scandle1 = None
scandle2 = None
scandle3 = None

sprice = 0
price = 0

k = 0


class RsRw(Strategy):

    def cal_RRSW(self):
        _TickerSMA = ta.sma(candles=self.candles, period=21)
        _TickerChange = self.close - _TickerSMA
        _RefCandles = self.get_candles(exchange='Binance Spot', symbol='USDT-DAI', timeframe='15m')
        _RefSMA = ta.sma(_RefCandles, period=21, source_type='close')
        _CurrentTime = self.candles
        _RefChange = ta.wclprice(candles=_RefCandles, sequential=False) - _RefSMA
        _AvgVol_long = ta.vwma(self.candles, period=5)
        _AvgVol_short = ta.vwma(self.candles, period=21)
        _VolWeight = _AvgVol_long / _AvgVol_short
        _RRSW = (_TickerChange / _TickerSMA - _RefChange / _RefSMA) * _VolWeight * 100
        self.log("The Current RRSW is " + str(_RRSW))
        return (_TickerChange / _TickerSMA - _RefChange / _RefSMA) * _VolWeight * 100

    def cal_changeRate(self):
        Y = np.array(lincandles)
        X = np.array(range(len(lincandles)))
        X = sm.add_constant(X)
        model = sm.OLS(Y, X)
        results = model.fit()
        rate = self.cal_RRSW() - results.params[0]
        self.log("The change rate is: " + str(rate))
        return rate

    def dna(self) -> str:
        return 'f)chh'

    def cal_certainty(self):
        c, s = pearsonr(rolling_change, rolling_RRSW)
        self.log("The certainty is: " + str(c))
        return c

    def hyperparameters(self) -> list:
        return [
            {'name': 'certainty_multiplier', 'type': float, 'min': 0, 'max': 1, 'default': 0.5822784810126582},
            {'name': 'positive_change_multiplier', 'type': float, 'min': 0, 'max': 1, 'default': 0.13924050632911392},
            {'name': 'negative_change_multiplier', 'type': float, 'min': -1, 'max': 0, 'default': 0},
            {'name': 'close_change_rate_multiplier', 'type': float, 'min': 0, 'max': 1, 'default': 0.02531645569620253},
            {'name': 'rolling_length', 'type': int, 'min': 8, 'max': 8, 'default': 8},
        ]

    # def dna(self) -> str:
    #     return 'j6an'
    # j6an 54.48% profit -10.63% drawdown

    def before(self) -> None:

        global lincandles
        linlength = 5
        while lincandles[linlength] is None:
            if lincandles[0] is None:
                lincandles[0] = self.cal_RRSW()
                return
            elif lincandles[1] is None:
                lincandles[1] = self.cal_RRSW()
                return
            elif lincandles[2] is None:
                lincandles[2] = self.cal_RRSW()
                return
            elif lincandles[3] is None:
                lincandles[3] = self.cal_RRSW()
                return
            elif lincandles[4] is None:
                lincandles[4] = self.cal_RRSW()
                return
            elif lincandles[5] is None:
                lincandles[5] = self.cal_RRSW()
                return
        self.log("Linlength complete")

        if lincandles[linlength] is not None:
            # Move the second value to the third and so on and make the first value self.cal_RRSW()
            lincandles[0] = lincandles[1]
            lincandles[1] = lincandles[2]
            lincandles[2] = lincandles[3]
            lincandles[3] = lincandles[4]
            lincandles[4] = lincandles[5]
            lincandles[5] = self.cal_RRSW()

        self.log("LinSort complete")

        # Change the values of Rolling_Change which is 21 in length, starting at zero replacing the values with
        # self.cal_changeRate()

        global rolling_change
        global rolling_RRSW
        global k

        while k <= self.hp['rolling_length']:
            rolling_change.insert(self.hp['rolling_length'] - k, self.cal_changeRate())
            rolling_RRSW.insert(self.hp['rolling_length'] - k, self.cal_RRSW())
            self.log("K is " + str(k))
            k += 1
            return

        self.log("Rolling complete")

        if len(rolling_change) >= self.hp['rolling_length']:
            # Move the second value to the third and so on and make the first value self.cal_changeRate()

            x = 0
            while x < self.hp['rolling_length']:
                rolling_change[x] = rolling_change[x + 1]
                rolling_RRSW[x] = rolling_RRSW[x + 1]
                x += 1
            rolling_change[self.hp['rolling_length']] = self.cal_changeRate()
            rolling_RRSW[self.hp['rolling_length']] = self.cal_RRSW()

            self.log("RollingSort complete")

    def should_long(self) -> bool:
        if len(rolling_change) >= self.hp['rolling_length']:
            if self.cal_changeRate() > self.hp['positive_change_multiplier'] and self.cal_certainty() > self.hp[
                'certainty_multiplier']:
                global echange
                echange = self.cal_changeRate()
                return True
            else:
                return False
            #
            #
            #
            # global candle1
            # global candle2
            # global candle3
            #
            # global price
            #
            # if candle1 is None and candle2 is None and candle3 is None:
            #     if self.cal_RRSW() > .75:
            #         candle1 = self.cal_RRSW()
            #         self.log("Testing at C1")
            #         return False
            # if candle1 is not None and candle2 is None and candle3 is None:
            #     # If cal_RRSW  is 10% greater than candle1
            #     if self.cal_RRSW() > candle1 * 1.05:
            #         candle2 = self.cal_RRSW()
            #         self.log("Testing at C2")
            #         return False
            #     else:
            #         candle1 = self.cal_RRSW()
            #         return False
            #
            # if candle1 is not None and candle2 is not None:
            #     price = self.close
            #     return True
            # else:
            #     candle2 = None
            #     candle3 = None
            #     if self.cal_RRSW() > 1:
            #         candle1 = self.cal_RRSW()
            #     else:
            #         candle1 = None
            #     return False

    def go_long(self):
        qty = round(self.balance / self.close) / 1.1
        self.buy = qty, self.close

    def should_short(self) -> bool:
        if len(rolling_change) >= self.hp['rolling_length']:
            # Move the second value to the third and so on and make the first value self.cal_changeRate(
            if self.cal_changeRate() < self.hp['negative_change_multiplier'] and self.cal_certainty() > self.hp[
                'certainty_multiplier']:
                global echange
                echange = self.cal_changeRate()
                return True
            else:
                return False
        # global scandle1
        # global scandle2
        # global scandle3
        #
        # global sprice
        #
        # if scandle1 is None and scandle2 is None and scandle3 is None:
        #     if self.cal_RRSW() < -.5:
        #         candle1 = self.cal_RRSW()
        #         self.log("Testing at short C1")
        #         return False
        # if scandle1 is not None and scandle2 is None and scandle3 is None:
        #     # If cal_RRSW  is 10% greater than candle1
        #     if self.cal_RRSW() < scandle1 * .95:
        #         scandle2 = self.cal_RRSW()
        #         self.log("Testing at short C2")
        #         return False
        #     else:
        #         scandle1 = self.cal_RRSW()
        #         return False
        # if scandle1 is not None and scandle2 is not None and scandle3 is None:
        #     if self.cal_RRSW() < scandle1 * .9:
        #         scandle3 = self.cal_RRSW()
        #         self.log("Testing at short C3")
        #     else:
        #         scandle2 = None
        #         scandle1 = self.cal_RRSW()
        #         return False
        #
        # if scandle1 is not None and scandle2 is not None and scandle3 is not None:
        #     sprice = self.close
        #     return True

    def go_short(self):
        qty = round(self.balance / self.close) / 1.1
        self.sell = qty, self.close

    def should_cancel_entry(self) -> bool:
        return False

    def update_position(self):
        global candle1
        global candle2
        global candle3

        global scandle2
        global scandle1
        global scandle3

        # two thirds of candle3
        if self.is_long:
            if self.cal_changeRate() < echange * self.hp['close_change_rate_multiplier'] or self.cal_certainty() < \
                    self.hp['certainty_multiplier']:
                self.log("Cancelling at C3")
                self.liquidate()
                candle3 = None
                scandle2 = None
                scandle1 = None
                return False
        if self.is_short:
            if self.cal_changeRate() > echange * self.hp['close_change_rate_multiplier'] or self.cal_certainty() < \
                    self.hp['certainty_multiplier']:
                self.log("Cancelling at C3")
                self.liquidate()
                candle3 = None
                scandle2 = None
                scandle1 = None
                return False
