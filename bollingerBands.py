from datetime import timedelta
import pandas as pd

class BollingerBands:
    
    def __init__(self, eventId, intervals):
        self.eventId = eventId
        self.time = eventId.matchOddsTime
        
        self.prices = eventId.prices
        self.homePrices = eventId.homeBackPrice
        self.awayPrices = eventId.awayBackPrice

        self.rowIndex = eventId.rowIndex
        
        self.homeMovingAverage = None
        self.homeOneStandardDev = None
        self.homeUpperStdDev = None
        self.homeLowerStdDev = None
        
        self.awayMovingAverage = None
        self.awayOneStandardDev = None
        self.awayUpperStdDev = None
        self.awayLowerStdDev = None
        
        ''' CHANGE THIS BACK TO FALSE'''
        if eventId.isInPlay == False: 
            # return print('Match not yet inplay')
            return None

        BollingerBands.loopThroughIntervals(self, eventId, intervals)

    ''' Create Bollinger bands for each time interval in the intervals list'''
    def loopThroughIntervals(self, eventId, intervals):
        self.eventId = eventId
        
        j = 0
        for interval in intervals:
            if (eventId.prices.iloc[-1:]['matchOddsTime'] - timedelta(seconds=interval)).values[0] - (eventId.prices.iloc[0:1]['matchOddsTime']).values[0] < 0:
                return    
            else:
                start = (eventId.prices.iloc[-1:]['matchOddsTime'] - timedelta(seconds=interval)).values[0]
                end = (eventId.prices.iloc[-1:]['matchOddsTime']).values[0]
                mask = (eventId.prices['matchOddsTime'] >= start) & (eventId.prices['matchOddsTime'] < end)
                self.sampleDf = eventId.prices.loc[mask].resample('S', on='matchOddsTime')['homeBackPrice', 'homeLayPrice', 'awayBackPrice', 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'].mean()

                self.homeMovingAverage = self.sampleDf['homeBackPrice'].mean()
                self.homeOneStandardDev = self.sampleDf['homeBackPrice'].std(ddof=0)
                self.awayMovingAverage = self.sampleDf['awayBackPrice'].mean()
                self.awayOneStandardDev = self.sampleDf['awayBackPrice'].std(ddof=0)

                # Average of standard deviation
                self.homeStdAverage = (self.homeOneStandardDev) + self.homeMovingAverage   
                self.awayStdAverage = (self.awayOneStandardDev) + self.awayMovingAverage    

                # Upper and lower bollinger bands
                self.homeUpperBand = self.homeMovingAverage + 2 * self.homeOneStandardDev
                self.homeLowerBand = self.homeMovingAverage - 2 * self.homeOneStandardDev
                self.awayUpperBand = self.awayMovingAverage + 2 * self.awayOneStandardDev
                self.awayLowerBand = self.awayMovingAverage - 2 * self.awayOneStandardDev
                
                # One standard deviation
                self.homeUpperStdDev  = self.homeMovingAverage + 1 * self.homeOneStandardDev
                self.homeLowerStdDev = self.homeMovingAverage - 1 * self.homeOneStandardDev 
                self.awayUpperStdDev  = self.awayMovingAverage + 1 * self.awayOneStandardDev
                self.awayLowerStdDev = self.awayMovingAverage - 1 * self.awayOneStandardDev 

                self.dfForAppending = pd.DataFrame([[self.rowIndex, end, self.homeMovingAverage, self.homeOneStandardDev, self.homeUpperBand, self.homeLowerBand,self.homeUpperStdDev, self.homeLowerStdDev, 
                                                     self.awayMovingAverage, self.awayOneStandardDev, self.awayUpperBand, self.awayLowerBand, self.awayUpperStdDev, self.awayLowerStdDev]],
                                                    columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                                             'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd'])

                eventId.bollingerBandDict[f'{str(interval)}'] = eventId.bollingerBandDict[f'{str(interval)}']._append(self.dfForAppending)

                BollingerBands.dataframeToCsv(self, intervals[j])
                j += 1
                 
    def dataframeToCsv(self, interval):
        self.dfForAppending.to_csv(f'./tempFiles/{self.eventId.fixture}_{interval}.csv', mode='a', header=False, index=False)
