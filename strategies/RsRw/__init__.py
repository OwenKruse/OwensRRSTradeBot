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
rolling_change = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None]
rolling_RRSW = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                None,
                None, None, None, None]

echange = None
scandle1 = None
scandle2 = None
scandle3 = None

sprice = 0
price = 0


class RsRw(Strategy):

    def cal_RRSW(self):
        _TickerSMA = ta.sma(candles=self.candles, period=21)
        _TickerChange = self.close - _TickerSMA
        _RefCandles = self.get_candles(exchange='Binance Spot', symbol='USDT-DAI', timeframe='5m')
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

    def cal_certainty(self):
        c, s = pearsonr(rolling_change, rolling_RRSW)
        self.log("The certainty is: " + str(c))
        return c

    def hyperparameters(self) -> list:
        return [
            {'name': 'certainty_multiplier', 'type': int, 'min': 0, 'max': 1, 'default': .95},
            {'name': 'positive_change_multiplier', 'type': float, 'min': 0, 'max': 1, 'default': .001},
            {'name': 'negative_change_multiplier', 'type': float, 'min': -1, 'max': 0, 'default': -.001},
            {'name': 'close_change_rate_multiplier', 'type': float, 'min': 0, 'max': 1, 'default': .95},

                ]

    def before(self) -> None:

        global lincandles
        while lincandles[5] is None:
            if lincandles[0] is None:
                lincandles[0] = self.cal_RRSW()
            elif lincandles[1] is None:
                lincandles[1] = self.cal_RRSW()
            elif lincandles[2] is None:
                lincandles[2] = self.cal_RRSW()
            elif lincandles[3] is None:
                lincandles[3] = self.cal_RRSW()
            elif lincandles[4] is None:
                lincandles[4] = self.cal_RRSW()
            elif lincandles[5] is None:
                lincandles[5] = self.cal_RRSW()

        if lincandles[5] is not None:
            # Move the second value to the third and so on and make the first value self.cal_RRSW()
            lincandles[0] = lincandles[1]
            lincandles[1] = lincandles[2]
            lincandles[2] = lincandles[3]
            lincandles[3] = lincandles[4]
            lincandles[4] = lincandles[5]
            lincandles[5] = self.cal_RRSW()

        # Change the values of Rolling_Change which is 21 in length, starting at zero replacing the values with
        # self.cal_changeRate()

        global rolling_change
        global rolling_RRSW
        while rolling_change[20] is None:
            if rolling_change[0] is None:
                rolling_change[0] = self.cal_changeRate()
                rolling_RRSW[0] = self.cal_RRSW()
            elif rolling_change[1] is None:
                rolling_change[1] = self.cal_changeRate()
                rolling_RRSW[1] = self.cal_RRSW()
            elif rolling_change[2] is None:
                rolling_change[2] = self.cal_changeRate()
                rolling_RRSW[2] = self.cal_RRSW()
            elif rolling_change[3] is None:
                rolling_change[3] = self.cal_changeRate()
                rolling_RRSW[3] = self.cal_RRSW()
            elif rolling_change[4] is None:
                rolling_change[4] = self.cal_changeRate()
                rolling_RRSW[4] = self.cal_RRSW()
            elif rolling_change[5] is None:
                rolling_change[5] = self.cal_changeRate()
                rolling_RRSW[5] = self.cal_RRSW()
            elif rolling_change[6] is None:
                rolling_change[6] = self.cal_changeRate()
                rolling_RRSW[6] = self.cal_RRSW()
            elif rolling_change[7] is None:
                rolling_change[7] = self.cal_changeRate()
                rolling_RRSW[7] = self.cal_RRSW()
            elif rolling_change[8] is None:
                rolling_change[8] = self.cal_changeRate()
                rolling_RRSW[8] = self.cal_RRSW()
            elif rolling_change[9] is None:
                rolling_change[9] = self.cal_changeRate()
                rolling_RRSW[9] = self.cal_RRSW()
            elif rolling_change[10] is None:
                rolling_change[10] = self.cal_changeRate()
                rolling_RRSW[10] = self.cal_RRSW()
            elif rolling_change[11] is None:
                rolling_change[11] = self.cal_changeRate()
                rolling_RRSW[11] = self.cal_RRSW()
            elif rolling_change[12] is None:
                rolling_change[12] = self.cal_changeRate()
                rolling_RRSW[12] = self.cal_RRSW()
            elif rolling_change[13] is None:
                rolling_change[13] = self.cal_changeRate()
                rolling_RRSW[13] = self.cal_RRSW()
            elif rolling_change[14] is None:
                rolling_change[14] = self.cal_changeRate()
                rolling_RRSW[14] = self.cal_RRSW()
            elif rolling_change[15] is None:
                rolling_change[15] = self.cal_changeRate()
                rolling_RRSW[15] = self.cal_RRSW()
            elif rolling_change[16] is None:
                rolling_change[16] = self.cal_changeRate()
                rolling_RRSW[16] = self.cal_RRSW()
            elif rolling_change[17] is None:
                rolling_change[17] = self.cal_changeRate()
                rolling_RRSW[17] = self.cal_RRSW()
            elif rolling_change[18] is None:
                rolling_change[18] = self.cal_changeRate()
                rolling_RRSW[18] = self.cal_RRSW()
            elif rolling_change[19] is None:
                rolling_change[19] = self.cal_changeRate()
                rolling_RRSW[19] = self.cal_RRSW()
            elif rolling_change[20] is None:
                rolling_change[20] = self.cal_changeRate()
                rolling_RRSW[20] = self.cal_RRSW()
        if rolling_change[20] is not None:
            # Move the second value to the third and so on and make the first value self.cal_changeRate()

            rolling_change[0] = rolling_change[1]
            rolling_change[1] = rolling_change[2]
            rolling_change[2] = rolling_change[3]
            rolling_change[3] = rolling_change[4]
            rolling_change[4] = rolling_change[5]
            rolling_change[5] = rolling_change[6]
            rolling_change[6] = rolling_change[7]
            rolling_change[7] = rolling_change[8]
            rolling_change[8] = rolling_change[9]
            rolling_change[9] = rolling_change[10]
            rolling_change[10] = rolling_change[11]
            rolling_change[11] = rolling_change[12]
            rolling_change[12] = rolling_change[13]
            rolling_change[13] = rolling_change[14]
            rolling_change[14] = rolling_change[15]
            rolling_change[15] = rolling_change[16]
            rolling_change[16] = rolling_change[17]
            rolling_change[17] = rolling_change[18]
            rolling_change[18] = rolling_change[19]
            rolling_change[19] = rolling_change[20]
            rolling_change[20] = self.cal_changeRate()

            rolling_RRSW[0] = rolling_RRSW[1]
            rolling_RRSW[1] = rolling_RRSW[2]
            rolling_RRSW[2] = rolling_RRSW[3]
            rolling_RRSW[3] = rolling_RRSW[4]
            rolling_RRSW[4] = rolling_RRSW[5]
            rolling_RRSW[5] = rolling_RRSW[6]
            rolling_RRSW[6] = rolling_RRSW[7]
            rolling_RRSW[7] = rolling_RRSW[8]
            rolling_RRSW[8] = rolling_RRSW[9]
            rolling_RRSW[9] = rolling_RRSW[10]
            rolling_RRSW[10] = rolling_RRSW[11]
            rolling_RRSW[11] = rolling_RRSW[12]
            rolling_RRSW[12] = rolling_RRSW[13]
            rolling_RRSW[13] = rolling_RRSW[14]
            rolling_RRSW[14] = rolling_RRSW[15]
            rolling_RRSW[15] = rolling_RRSW[16]
            rolling_RRSW[16] = rolling_RRSW[17]
            rolling_RRSW[17] = rolling_RRSW[18]
            rolling_RRSW[18] = rolling_RRSW[19]
            rolling_RRSW[19] = rolling_RRSW[20]
            rolling_RRSW[20] = self.cal_RRSW()

    def should_long(self) -> bool:
        if rolling_change[20] is not None:
            if self.cal_changeRate() > self.hp['positive_change_multiplier'] and self.cal_certainty() > self.hp['certainty_multiplier']:
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
        qty = round(self.balance / self.close) / 1.5
        self.buy = qty, self.close

    def should_short(self) -> bool:
        if rolling_change[20] is not None:
            # Move the second value to the third and so on and make the first value self.cal_changeRate(
            if self.cal_changeRate() < self.hp['negative_change_multiplier'] and self.cal_certainty() > self.hp['certainty_multiplier']:
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
        qty = round(self.balance / self.close) / 1.5
        self.sell = qty, self.close

    def should_cancel_entry(self) -> bool:
        return False



    # def hyperparameters(self) -> list:
    #     return [
    #         {'name': 'emultiple', 'type': 'float', 'min': 0, 'max': 1, 'default': .95},
    #
    #     ]

    def update_position(self):
        global candle1
        global candle2
        global candle3

        global scandle2
        global scandle1
        global scandle3

        # two thirds of candle3
        if self.is_long:
            if self.cal_changeRate() < echange * self.hp['close_change_rate_multiplier'] or self.cal_certainty() < 0.95:
                self.log("Cancelling at C3")
                self.liquidate()
                candle3 = None
                scandle2 = None
                scandle1 = None
                return False
        if self.is_short:
            if self.cal_changeRate() > echange * self.hp['close_change_rate_multiplier'] or self.cal_certainty() < 0.95:
                self.log("Cancelling at C3")
                self.liquidate()
                candle3 = None
                scandle2 = None
                scandle1 = None
                return False
