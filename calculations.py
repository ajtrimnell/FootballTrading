from datetime import timedelta
import math
from datetime import datetime
import csv

class Calculations:
    
    def __init__(self, eventId, intervals, betAngelApiObject, matchObjectsList, now):
        self.eventId = eventId
        self.homeXg = eventId.homeXg
        self.awayXg = eventId.awayXg
        self.minOfMatchSeconds = math.ceil(eventId.rowIndex)
        self.minOfMatch = math.ceil(eventId.rowIndex / 60)
        self.rowIndex = eventId.rowIndex
        self.interval = None
        
        self.homeXgForPeriod = None
        self.awayXgForPeriod = None
        
        self.homeLayOpportunity = False
        self.awayLayOpportunity = False
    
        def goalCalculations(self, eventId, intervals):        
            # Sometimes, when markets are deleted from Bet Angel Guardian, they still appear when the markets are pulled in via the api.
            # This will delete any events that are not in Guardian but appear in the match objects list
            if len(eventId.prices['matchOddsTime']) == 0 and (eventId.dateTimeObject - now).total_seconds() < 0:
                if eventId.matchStatus == 'NS':
                    return print('Match not yet started')
                else:
                    matchObjectsList.remove(eventId)
                    return ['Bet Angel Api thinks market is still loaded in', 0]
            if eventId.matchStatus == 'NS':
                return
            
            for interval in intervals:
                self.interval = interval
                if (eventId.prices.iloc[-1:]['matchOddsTime'] - timedelta(seconds=interval)).values[0] - (eventId.prices.iloc[0:1]['matchOddsTime']).values[0] < interval:
                    return    
                else:
                    matchStartTime = (eventId.prices.iloc[0:1]['matchOddsTime']).values[0]

                    self.minOfMatch = math.ceil(((eventId.prices.iloc[-1:]['matchOddsTime'] - matchStartTime).values[0]).astype('float64')/1e9/60)
                    self.start = (eventId.prices.iloc[-1:]['matchOddsTime'] - timedelta(seconds=interval)).values[0]
                    self.end = (eventId.prices.iloc[-1:]['matchOddsTime']).values[0]
                    
                    self.homeBackPrice = eventId.prices.iloc[-1:]['homeBackPrice']
                    self.homeLayPrice = eventId.prices.iloc[-1:]['homeLayPrice']
                    self.awayLayPrice = eventId.prices.iloc[-1:]['awayLayPrice']
                    self.awayBackPrice = eventId.prices.iloc[-1:]['awayBackPrice']
                    
                    self.mask = (eventId.prices['matchOddsTime'] >= self.start) & (eventId.prices['matchOddsTime'] < self.end)
                    self.bollingerMask = (eventId.bollingerBandDict[f'{str(self.interval)}']['matchTime'] >= self.start) & (eventId.bollingerBandDict[f'{str(self.interval)}']['matchTime'] < self.end)
                    self.maskHomePlusOne = (eventId.pricesPlusOneToHome['matchOddsTime'] >= self.start) & (eventId.pricesPlusOneToHome['matchOddsTime'] < self.end)
                    self.maskAwayPlusOne = (eventId.pricesPlusOneToAway['matchOddsTime'] >= self.start) & (eventId.pricesPlusOneToAway['matchOddsTime'] < self.end)
                    
                    self.sampleMatchPrices = eventId.prices.loc[self.mask].resample('S', on='matchOddsTime')['homeBackPrice', 'homeLayPrice', 'awayBackPrice', 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'].mean()
                    self.sampleHomePlusOne = eventId.pricesPlusOneToHome.loc[self.maskHomePlusOne].resample('S', on='matchOddsTime')[f'{eventId.homeTeam}_back', f'{eventId.homeTeam}_lay', f'{eventId.awayTeam}_back', f'{eventId.awayTeam}_lay', 'drawBackPrice', 'drawLayPrice'].mean()
                    self.sampleAwayPlusOne = eventId.pricesPlusOneToAway.loc[self.maskAwayPlusOne].resample('S', on='matchOddsTime')[f'{eventId.awayTeam}_back', f'{eventId.awayTeam}_lay', f'{eventId.homeTeam}_back', f'{eventId.homeTeam}_lay', 'drawBackPrice', 'drawLayPrice'].mean()
                
                    self.homeBackAverage = self.sampleMatchPrices.iloc[-10:-1]['homeBackPrice'].mean()
                    self.awayBackAverage = self.sampleMatchPrices.iloc[-10:-1]['awayBackPrice'].mean()
                    
                    self.homeUpperBand = eventId.bollingerBandDict[f'{str(self.interval)}'].iloc[-1:]['homeUpperBand'].values[0]
                    self.awayUpperBand = eventId.bollingerBandDict[f'{str(self.interval)}'].iloc[-1:]['awayUpperBand'].values[0]
   
                    self.minOfIntervalStart = math.ceil(((self.sampleMatchPrices.iloc[0:1].index - matchStartTime).values[0]).astype('float64')/1e9/60)
                    
                    self.xgsForPeriod = xgForPeriod(self)
                    self.plusOneMovingAverages = plusOneMovingAverage(self)
                    self.goalPriceMovements = pricesAtPeriodStart(self)
                    
                    ''' Lay bet placed on home team '''
                    self.homeLay_homeGoal = profitOrLossIfGoal(self, self.sampleHomePlusOne, eventId.homeTeam, 'homeLayPrice')
                    self.homeLay_awayGoal = profitOrLossIfGoal(self, self.sampleAwayPlusOne, eventId.homeTeam, 'homeLayPrice')
                    
                    ''' Lay bet placed on away team '''
                    self.awayLay_homeGoal = profitOrLossIfGoal(self, self.sampleHomePlusOne, eventId.awayTeam, 'awayLayPrice')
                    self.awayLay_awayGoal = profitOrLossIfGoal(self, self.sampleAwayPlusOne, eventId.awayTeam, 'awayLayPrice')
                           
                    self.totalLossHomeLay = averageLossForPeriodHomeLay(self.xgsForPeriod, self.homeLay_homeGoal, self.homeLay_awayGoal).values
                    self.totalLossAwayLay = averageLossForPeriodAwayLay(self.xgsForPeriod, self.awayLay_homeGoal, self.awayLay_awayGoal).values

                    self.bollingerBandDataframe = bollingerBands(self)
                    self.breakEvenPriceHomeLay = breakEvenCalcsHomeLay(self)
                    self.breakEvenPriceAwayLay = breakEvenCalcsAwayLay(self)
                    
                    self.homeLayOpportunity = checkForOpportunity(self, self.homeBackAverage, self.priceHomeLay, self.homeUpperBand, \
                                                                  'homeBackPrice', 'homeMovingAverage', 'awayBackPrice')
                    self.awayLayOpportunity = checkForOpportunity(self, self.awayBackAverage, self.priceAwayLay, self.awayUpperBand, \
                                                                  'awayBackPrice', 'awayMovingAverage', 'homeBackPrice')

                                
        def checkForOpportunity(self, teamBackAverage, priceTeamLay, teamUpperBand, teamBackPrice, teamMovingAverage, otherTeamBackPrice):
            a = placeBetCalcs(teamBackAverage, priceTeamLay)
            b = otherTeamPriceGradient(otherTeamBackPrice)
            c = teamVolatility(teamBackAverage, teamUpperBand)
            d = priceSpikes(self, teamBackAverage, teamBackPrice, teamMovingAverage)
            e = bettingInfo(self)
            f = checkMatchScore()
            g = marketLastSuspended()
            

            with open(f'test/{eventId.fixture}.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([now,self.interval,a,b,c,d,e,f,g])
            
            if placeBetCalcs(teamBackAverage, priceTeamLay) == True:
                if otherTeamPriceGradient(otherTeamBackPrice) == True:
                    if teamVolatility(teamBackAverage, teamUpperBand) == True:   
                        if priceSpikes(self, teamBackAverage, teamBackPrice, teamMovingAverage) == True:
                            if bettingInfo(self) == True:
                                if checkMatchScore() == True:
                                    if marketLastSuspended() == True:
                                        print('It worked')      
                                        return True
            return False

        def xgForPeriod(self):
            # Calculate the xg at the start and end of the interval to get the expected goals during that period
            self.homeXgForPeriod = (xGRemaining(self.homeXg, self.minOfIntervalStart)) - xGRemaining(self.homeXg, self.minOfMatch)
            self.awayXgForPeriod = (xGRemaining(self.awayXg, self.minOfIntervalStart)) - xGRemaining(self.awayXg, self.minOfMatch)
            return self.homeXgForPeriod, self.awayXgForPeriod
        
        def xGRemaining(xg, minOfMatch):
            return ((1-((1/95*minOfMatch))**.84) * xg)
        
        def plusOneMovingAverage(self):
            self.movingAveragePlusOneToHome_homeBack = self.sampleHomePlusOne.iloc[0:-1][f'{eventId.homeTeam}_back'].mean()
            self.movingAveragePlusOneToHome_awayBack = self.sampleHomePlusOne.iloc[0:-1][f'{eventId.awayTeam}_back'].mean()
            self.movingAveragePlusOneToHome_drawBack = self.sampleHomePlusOne.iloc[0:-1]['drawBackPrice'].mean()
            
            self.movingAveragePlusOneToHome_homeLay = self.sampleHomePlusOne.iloc[0:-1][f'{eventId.homeTeam}_lay'].mean()
            self.movingAveragePlusOneToHome_awayLay = self.sampleHomePlusOne.iloc[0:-1][f'{eventId.awayTeam}_lay'].mean()
            self.movingAveragePlusOneToHome_drawLay = self.sampleHomePlusOne.iloc[0:-1]['drawLayPrice'].mean()
            
            return self.movingAveragePlusOneToHome_homeBack, self.movingAveragePlusOneToHome_awayBack, self.movingAveragePlusOneToHome_drawBack, \
                    self.movingAveragePlusOneToHome_homeLay, self.movingAveragePlusOneToHome_awayLay, self.movingAveragePlusOneToHome_drawLay
        
        def pricesAtPeriodStart(self):
            self.homeStartBackPrice = self.sampleMatchPrices.iloc[0:1]['homeBackPrice']
            self.awayStartBackPrice = self.sampleMatchPrices.iloc[0:1]['awayBackPrice']
            self.drawStartBackPrice = self.sampleMatchPrices.iloc[0:1]['drawBackPrice']
            return self.homeStartBackPrice, self.awayStartBackPrice, self.drawStartBackPrice
            
        def profitOrLossIfGoal(self, plusOneMarket, team, pricesDfColumn):
            x = plusOneMarket.iloc[-1][f'{team}_back']-1
            y = self.sampleMatchPrices.iloc[0:1][pricesDfColumn]-1
            z = plusOneMarket.iloc[-1][f'{team}_back']
            ''' Example
            x = self.sampleHomePlusOne.iloc[-1][f'{eventId.homeTeam}_back']-1
            y = self.sampleMatchPrices.iloc[0:1]['homeLayPrice']-1
            z = self.sampleHomePlusOne.iloc[-1][f'{eventId.homeTeam}_back']
            '''
            return (x - y) / z
            
        def averageLossForPeriodHomeLay(xgsForPeriod, homeLay_homeGoal, homeLay_awayGoal):
            return xgsForPeriod[0]*homeLay_homeGoal + xgsForPeriod[1]*homeLay_awayGoal
        
        def averageLossForPeriodAwayLay(xgsForPeriod, awayLay_homeGoal, awayLay_awayGoal):
            return xgsForPeriod[0]*awayLay_homeGoal + xgsForPeriod[1]*awayLay_awayGoal
        
        def bollingerBands(self):
            self.bollingerBandDataframe = eventId.bollingerBandDict[f'{str(self.interval)}']
            return self.bollingerBandDataframe
 
        def breakEvenCalcsHomeLay(self):         
            self.breakEvenHomeLay = self.totalLossHomeLay
            self.priceHomeLay = self.sampleMatchPrices.iloc[0:1]['homeBackPrice']
            self.initialPrice = self.sampleMatchPrices.iloc[0:1]['homeBackPrice'] # Price at the start of the interval
            while self.breakEvenHomeLay[0] < 0:
                self.breakEvenHomeLay += 0.01 / 60
                self.breakEvenHomeLay = self.breakEvenHomeLay + (((self.priceHomeLay-1) - (self.initialPrice-1)) / self.priceHomeLay)
            return self.breakEvenHomeLay
        
        def breakEvenCalcsAwayLay(self):
            self.breakEvenAwayLay = self.totalLossAwayLay
            self.priceAwayLay = self.sampleMatchPrices.iloc[0:1]['awayBackPrice']
            self.initialPrice = self.sampleMatchPrices.iloc[0:1]['awayBackPrice'] # Price at the start of the interval
            while self.breakEvenAwayLay[0] < 0:
                self.priceAwayLay += 0.01 / 60
                self.breakEvenAwayLay = self.breakEvenAwayLay + (((self.priceAwayLay-1) - (self.initialPrice-1)) / self.priceAwayLay)
            return self.priceAwayLay
                
        def placeBetCalcs(teamBackAverage, priceTeamLay):
            if teamBackAverage - priceTeamLay.values[0] < 0:
                return False
            if teamBackAverage - priceTeamLay.values[0] >= 0:
                return True

        def otherTeamPriceGradient(teamBackPrice):
            teamGradientRange = eventId.prices.loc[self.mask].resample('S', on='matchOddsTime')['matchOddsTime',f'{teamBackPrice}'].mean()
            teamGradient = (teamGradientRange.iloc[-1:][f'{teamBackPrice}'].values[0] - teamGradientRange.iloc[0:1][f'{teamBackPrice}'].values[0]) / \
                            (teamGradientRange.iloc[-1:]['matchOddsTime'].values[0] - teamGradientRange.iloc[0:1]['matchOddsTime'].values[0]).astype('float64')/1e9/60
            if teamGradient < 0:
                return True
            return False

        def teamVolatility(teamBackAverage, teamUpperBand):
            if teamBackAverage < teamUpperBand:
                return True
            return False

        def priceSpikes(self, teamBackAverage, teamBackPrice, teamMovingAverage):
            spikePriceUp = teamBackAverage * 1.15
            spikePriceDown = teamBackAverage * 0.85
            # Get the min and max prices during the interval
            minPrice = self.sampleMatchPrices[f'{teamBackPrice}'].min()
            maxPrice = self.sampleMatchPrices[f'{teamBackPrice}'].max()
            
            if maxPrice > spikePriceUp or minPrice < spikePriceDown:
                return False
            if self.sampleMatchPrices.iloc[-1:][f'{teamBackPrice}'].values[0] < self.bollingerBandDataframe.iloc[-1:][f'{teamMovingAverage}'].values[0]:
                return False
            return True

        def bettingInfo(self):
            self.storedValues = betAngelApiObject.storedValues(eventId.id)
            currentMarketLiability = self.storedValues['result']['markets'][0]['sharedValues'][0]['v']
            greeningProfitOrLoss = self.storedValues['result']['markets'][0]['selections'][0]['sharedValues'][0]['v']
            
            try:
                x = greeningProfitOrLoss / currentMarketLiability
                
                if x > 0.9 or x < 1.1: 
                    return True
                else:
                    return False
            except ZeroDivisionError:
                return True
                        
        def checkMatchScore():
            if eventId.homeGoals == 0 and eventId.awayGoals == 0:
                return True
            else:
                return False
            
        def marketLastSuspended():
            file = open(f'C:/dev/Python/betfairData/marketStatusCsvs/status_{eventId.id}_{eventId.homeTeam} v {eventId.awayTeam} - match Odds.csv')
            content = file.read().split('\n')
            content.reverse()
            for row in range(1, len(content)-1):
                content[row] = content[row].split(',')
                if content[row][-2] == '1':
                    now = datetime.now()
                    dateTimeObject = datetime.strptime(content[row][0],'%d/%m/%Y %H:%M:%S')
                    if (now - dateTimeObject).total_seconds() > 300:
                        return True
                    else:
                        return False

        goalCalculations(self, eventId, intervals)
        
    def checkOpportunityValue(self):
        return [self.homeLayOpportunity, self.awayLayOpportunity]
    
    def calculateStake(self, team, fixture, dateTimeObject, calcInstance):
        if team == 'home':
            layStake = 4 / (self.homeBackPrice.values[0] - 1)
        elif team == 'away':
            layStake = 4 / (self.homeAwayPrice.values[0] - 1)
        else:
            return print('Stake calculation error')
        # Back stake is one fifth of the total liability
        backStake = 1
        
        with open('opportunities.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([fixture, dateTimeObject, calcInstance])
        
        return [layStake, backStake]
        
    





class PositionExit:
    
    def __init__(self, eventId, intervals, betAngelApiObject, matchObjectsList, now):
        
        self.matchScoreList = eventId.matchScoreList
        
        
    # Check for home goal
    # Check for away goal
    
        
