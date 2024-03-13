import requests
from pprint import pprint
import numpy as np
from datetime import datetime, timedelta
import time
import pandas as pd
import csv
import os
import math

from teamsCountries import *

class CallBetfair:

    def __init__(self, matchOddsPort, matchOddsPlusOnePort, correctScorePort, goalMarketsPort):
        self.response = None 
        self.matchOddsPort = matchOddsPort
        self.matchOddsPlusOnePort = matchOddsPlusOnePort
        self.correctScorePort = correctScorePort
        self.goalMarketsPort = goalMarketsPort
        
    def request(endpoint, dataRequired, port, path):
        apiUrl = f"http://localhost:{port}/api/{path}/v1.0/{endpoint}" 
        response = (requests.post(apiUrl, headers = {'Content-Type': 'application/json'}, data=dataRequired)).json()
        return response

    def markets(self):  
        endpoint = "getMarkets"      
        dataRequired = '{"dataRequired":["ID","NAME","MARKET_START_TIME","MARKET_INPLAY_STATUS","EVENT_ID","EVENT_TYPE_ID","MARKET_TYPE","SELECTION_IDS","SELECTION_NAMES"]}' 
        return (CallBetfair.request(endpoint, dataRequired, self.matchOddsPort, 'markets')).get('result',{}).get('markets')
    
    def marketPrices(self):
        endpoint = "getStoredValues"
        dataRequired = '{"marketsFilter":{"filter":"ALL"},"selectionsFilter":{"filter":"ALL"},"storedValueFilterBetAngelLevel":{"storedValueFilter":"ALL","excludeSharedValues":true},"storedValueFilterEventLevel":{"storedValueFilter":"ALL","excludeSharedValues":true},"storedValueFilterMarketLevel":{"storedValueFilter":"ALL","excludeSharedValues":true},"storedValueFilterSelectionLevel":{"storedValueFilter":"ALL","excludeSharedValues":true}}'
        return CallBetfair.request(endpoint, dataRequired, self.matchOddsPort, 'automation').get('result',{}).get('markets')
    
    def plusOneMarkets(self):
        endpoint = "getMarkets"      
        dataRequired = '{"dataRequired":["ID","NAME","MARKET_START_TIME","MARKET_INPLAY_STATUS","EVENT_ID","EVENT_TYPE_ID","MARKET_TYPE","SELECTION_IDS","SELECTION_NAMES"]}' 
        return (CallBetfair.request(endpoint, dataRequired, self.matchOddsPlusOnePort, 'markets')).get('result',{}).get('markets')
    
    def plusOneMarketPrices(self):
        endpoint = "getStoredValues"
        dataRequired = '{"marketsFilter":{"filter":"ALL"},"selectionsFilter":{"filter":"ALL"},"storedValueFilterBetAngelLevel":{"storedValueFilter":"ALL","excludeSharedValues":true},"storedValueFilterEventLevel":{"storedValueFilter":"ALL","excludeSharedValues":true},"storedValueFilterMarketLevel":{"storedValueFilter":"ALL","excludeSharedValues":true},"storedValueFilterSelectionLevel":{"storedValueFilter":"ALL","excludeSharedValues":true}}'
        return CallBetfair.request(endpoint, dataRequired, self.matchOddsPlusOnePort, 'automation').get('result',{}).get('markets')
    
    
    def goalMarkets(self):
        endpoint = "getMarkets"      
        dataRequired = '{"dataRequired":["ID","MARKET_INPLAY_STATUS","EVENT_ID","MARKET_TYPE"]}' 
        return CallBetfair.request(endpoint, dataRequired, self.goalMarketsPort, 'markets').get('result',{}).get('markets')
    
    def correctScore(self):
        endpoint = "getMarkets"      
        dataRequired = '{"dataRequired":["ID","MARKET_INPLAY_STATUS","EVENT_ID","MARKET_TYPE"]}' 
        return CallBetfair.request(endpoint, dataRequired, self.correctScorePort, 'markets').get('result',{}).get('markets')
    
    def __repr__(self):
        return self.markets


def createBetAngelApiObject(): 
    ''' 
    Ports:
    9000 - Match odds
    9001 - Match odds +1
    9002 - Correct score - Currently getting the xg from a csv, so this redundant
    9003 - Goal markets
    '''
    callBetfairObject = CallBetfair(9000,9001,9002,9003)
    return callBetfairObject

''' Create an object that will be used for all api calls. This means that only one object is created daily '''
betAngelApiObject = createBetAngelApiObject()


class Match:
    
    def __init__(self, id, eventId, fixture, dateTimeString, selections, isInPlay):
        
        self.rowIndex = 0
        self.isAboutToStart = False
        
        self.id = id
        self.plusOneToHomeId = None
        self.plusOneToAwayId = None
        self.eventId = eventId 
        self.rapidApiId = None
        
        self.fixture = fixture
        self.csFixture = fixture # For getting correct score csv file
        
        self.homeTeam = None
        self.awayTeam = None 
        self.homeTeamCountry = None
        self.awayTeamCountry = None
        
        self.matchDate = None
        self.startTime = None
        self.dateTimeObject = None
        
        self.isInPlay = isInPlay
        self.matchMinute = 0
        self.matchScore = (0,0)
        self.homeGoals = None
        self.awayGoals = None
         
        self.homeXg = None
        self.awayXg = None
        
        self.matchOddsTime = np.ndarray(shape=(9000, 1), dtype='U33')

        self.homeBackPrice = np.ndarray(shape=(9000), 
                                        dtype= 'float')
        self.homeLayPrice = np.ndarray(shape=(9000), 
                                        dtype= 'float')
        self.awayBackPrice = np.ndarray(shape=(9000), 
                                        dtype= 'float')
        self.awayLayPrice = np.ndarray(shape=(9000), 
                                        dtype= 'float')
        self.drawBackPrice = np.ndarray(shape=(9000), 
                                        dtype= 'float')
        self.drawLayPrice = np.ndarray(shape=(9000), 
                                        dtype= 'float')
    
        self.prices = pd.DataFrame(columns=['rowIndex', 'matchOddsTime', 'homeBackPrice', 'homeLayPrice', 'awayBackPrice', 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'])
   
        self.bollingerBands300 = pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
        self.bollingerBands360 = pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
        self.bollingerBands420 = pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
        self.bollingerBands480 = pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
        self.bollingerBands540 = pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
        self.bollingerBands600 = pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
        self.bollingerBands660 = pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
        self.bollingerBands720 = pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
        self.bollingerBands780 = pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
        self.bollingerBands840 = pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
        self.bollingerBands900 = pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
        self.bollingerBands960 = pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
        self.bollingerBands1020 = pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
        self.bollingerBands1080 = pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
        self.bollingerBands1120 = pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
        self.bollingerBands1200 = pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
      
        self.bollingerBands10 = pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])

        self.betPlaced = False
        self.positionExited = False

        def fixtureParse(self, fixture):
            self.fixture = (fixture.split(' - '))[0]
            self.csFixture = self.fixture + ' - ' + 'Correct Score'
            self.fixture = self.fixture.replace(' v ', '_v_')
            return self.fixture, self.csFixture
        
        def matchDateTime(self, dateTimeString):
            self.dateTimeObject = datetime.strptime(dateTimeString.replace('T', ' ').replace('+00:00', ''), '%Y-%m-%d %H:%M:%S')
            return self.dateTimeObject         
        
        def dateAndTime(self, dateTimeString):
            self.matchDate = (dateTimeString.split('T'))[0]
            self.startTime = ((dateTimeString.split('T'))[1].split('+'))[0]
            return self.matchDate, self.startTime

        def teams(self, selections):
            self.homeId = selections[0].get('id')
            self.homeTeam = selections[0].get('name')
            self.awayId = selections[1].get('id')
            self.awayTeam = selections[1].get('name')
            return self.homeId, self.homeTeam, self.awayId, self.awayTeam
        
        def teamsCountry(self):
            self.homeTeamCountry = countries[self.homeTeam]
            self.awayTeamCountry = countries[self.awayTeam]
            
        def createCsvs(self):
            self.prices.to_csv(f'./tempFiles/{self.fixture}_prices.csv')
            self.bollingerBands10.to_csv(f'./tempFiles/{self.fixture}_10.csv')
            self.bollingerBands10.to_csv(f'./tempFiles/{self.fixture}_300.csv')

        def plusOneCsvs(self):
            self.pricesPlusOneToHome.to_csv(f'./plusOneMarkets/{self.fixture}_{self.homeTeam}_plus_one.csv')
            self.pricesPlusOneToAway.to_csv(f'./plusOneMarkets/{self.fixture}_{self.awayTeam}_plus_one.csv')

        def plusOneDataframes(self):
            self.pricesPlusOneToHome = pd.DataFrame(columns=['rowIndex', 'matchOddsTime', f'{self.homeTeam}_back', f'{self.homeTeam}_lay', f'{self.awayTeam}_back', f'{self.awayTeam}_lay', 'drawBackPrice', 'drawLayPrice'])
            self.pricesPlusOneToAway = pd.DataFrame(columns=['rowIndex', 'matchOddsTime', f'{self.awayTeam}_back', f'{self.awayTeam}_lay', f'{self.homeTeam}_back', f'{self.homeTeam}_lay', 'drawBackPrice', 'drawLayPrice'])
            
 
        fixtureParse(self, fixture)
        dateAndTime(self, dateTimeString)
        matchDateTime(self, dateTimeString)
        teams(self, selections)
        teamsCountry(self)
        createCsvs(self)
        plusOneDataframes(self)
        plusOneCsvs(self)
        
       
    def __repr__(self):
        return self.eventId
          
    def getXg(self):
        try:
            file = open(f'./xgFiles/_{self.csFixture}.csv', mode='r')
        except FileNotFoundError:
            return print(f'{self.csFixture} file not found')
        
        content = file.read().split('\n')
        content[1] = content[1].split(',')

        self.homeXg = round(float(content[1][8]), 2)
        self.awayXg = round(float(content[1][6]), 2)
        return self.homeXg, self.awayXg


class MatchPrices:

    def __init__(self, now):
        self.latestOdds = betAngelApiObject.marketPrices()
        self.marketLatestOdds = None
        self.now = now
        
        ''' Check if the market has finished and is now closed'''
        def currentMatchOdds(self):
            for odds in self.latestOdds:
                for match in matchObjectsList:
                    if match.id == odds.get('id') and odds.get('status') != 'CLOSED': 
                        pricesMatchOdds(match, odds) 
                        if checkForTimeGaps(match) != 0:           
                             break
                        break

        def checkForTimeGaps(match):
            self.prices = match.prices
            self.eventId = match.eventId

            if len(match.prices['matchOddsTime']) == 0:
                matchObjectsList.remove(match.eventId)
                return print('Bet Angel Api thinks market is still loaded in')
          
            self.startTime = match.prices['matchOddsTime'][0]
            self.currentTime = match.prices.iloc[-1, 1]
            
            if match.rowIndex - (self.currentTime - self.startTime).total_seconds() != 1:
                MatchPrices.changeTimeData(self, match)
                print('Time is corrupted', match.rowIndex - (self.currentTime - self.startTime).total_seconds(), self.startTime, self.currentTime, match.rowIndex, self.eventId.matchOddsTime[self.eventId.rowIndex-1][0])
                return 0
        
        def pricesMatchOdds(match, odds):
            match.prices = match.prices._append(pd.DataFrame([[match.rowIndex, self.now, 
                                odds.get('selections', {})[0].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[0].get('instances')[0].get('values')[1].get('v'),
                                odds.get('selections', {})[1].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[1].get('instances')[0].get('values')[1].get('v'),
                                odds.get('selections', {})[2].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[2].get('instances')[0].get('values')[1].get('v')]],
                                columns=['rowIndex', 'matchOddsTime', 'homeBackPrice', 'homeLayPrice', 'awayBackPrice', 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'],
                                ),ignore_index = True)      
            
            self.dfToAppend = pd.DataFrame([[match.rowIndex, self.now, 
                                odds.get('selections', {})[0].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[0].get('instances')[0].get('values')[1].get('v'),
                                odds.get('selections', {})[1].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[1].get('instances')[0].get('values')[1].get('v'),
                                odds.get('selections', {})[2].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[2].get('instances')[0].get('values')[1].get('v')]],
                                columns=['rowIndex', 'matchOddsTime', 'homeBackPrice', 'homeLayPrice', 'awayBackPrice', 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'])
            
            MatchPrices.dataframeToCsv(self, match)
                
            match.rowIndex += 1
            
            return 

        currentMatchOdds(self)
           
    def dataframeToCsv(self, match):
        self.dfToAppend.to_csv(f'./tempFiles/{match.fixture}_prices.csv', mode='a', header=False, index=False)
  
  
    def changeTimeData(self, match):
        self.eventId = match
        self.rowToAppend = pd.DataFrame([match.prices.iloc[match.rowIndex-1]],
                                        columns=['matchOddsTime', 'homeBackPrice', 'homeLayPrice', 'awayBackPrice',
                                                 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'])

        match.prices.iloc[-1, 1] = match.prices.iloc[-1, 1] - timedelta(seconds=1)
        
        MatchPrices.duplicatePriceRow(self, self.rowToAppend, self.eventId)
        
        match.rowIndex += 1

    def duplicatePriceRow(self, rowToAppend, eventId):
        self.eventId = eventId
        self.rowToAppend = rowToAppend
        self.eventId.prices = pd.concat([self.eventId.prices, self.rowToAppend], 
                                        ignore_index = True, axis=0)
        

def matchObjects(betAngelApiObject):
    matchObjectsList = []
    for match in betAngelApiObject.markets():
        if match.get('eventId') == None:
            print('Market is closed')
            continue
        else:
            matchObjectsList.append(Match(match.get('id'), match.get('eventId'), match.get('name'), match.get('startTime'), match.get('selections'), match.get('inPlay')))
    return matchObjectsList


class MatchOddsPlusOne:
    
    def __init__(self, now):
        self.plusOneMarkets = betAngelApiObject.plusOneMarkets()
        self.latestOddsPlusOne = betAngelApiObject.plusOneMarketPrices()
        self.now = now
        
        def marketChanges(self):
            for match in matchObjectsList:
                if match.plusOneToHomeId == None and match.plusOneToHomeId == None:
                    MatchOddsPlusOne.matchMarketIds(self)
        
        def currentMatchOddsPlusOne(self):
            for odds in self.latestOddsPlusOne:
                for match in matchObjectsList:
                    if match.plusOneToHomeId == odds.get('id') and odds.get('status') != 'CLOSED': 
                        pricesHomeTeamPlusOne(match, odds, match.homeTeam)
                        break
                    if match.plusOneToAwayId == odds.get('id') and odds.get('status') != 'CLOSED': 
                        pricesAwayTeamPlusOne(match, odds, match.awayTeam)
                        break        
        
        def pricesHomeTeamPlusOne(match, odds, homeTeam):
            dataframeToAppend(match, odds, homeTeam)
            return
        
        def pricesAwayTeamPlusOne(match, odds, AwayTeam):
            dataframeToAppend(match, odds, AwayTeam)
            return
        
        def dataframeToAppend(match, odds, team):
            if team == match.homeTeam:
                match.pricesPlusOneToHome = match.pricesPlusOneToHome._append(pd.DataFrame([[match.rowIndex, self.now, 
                                    odds.get('selections', {})[0].get('instances')[0].get('values')[0].get('v'),
                                    odds.get('selections', {})[0].get('instances')[0].get('values')[1].get('v'),
                                    odds.get('selections', {})[1].get('instances')[0].get('values')[0].get('v'),
                                    odds.get('selections', {})[1].get('instances')[0].get('values')[1].get('v'),
                                    odds.get('selections', {})[2].get('instances')[0].get('values')[0].get('v'),
                                    odds.get('selections', {})[2].get('instances')[0].get('values')[1].get('v')]],
                                    columns=['rowIndex', 'matchOddsTime', f'{match.homeTeam}_back', f'{match.homeTeam}_lay', f'{match.awayTeam}_back', f'{match.awayTeam}_lay', 'drawBackPrice', 'drawLayPrice'],
                                    ),ignore_index = True)
            else:
                match.pricesPlusOneToAway = match.pricesPlusOneToAway._append(pd.DataFrame([[match.rowIndex, self.now, 
                                    odds.get('selections', {})[0].get('instances')[0].get('values')[0].get('v'),
                                    odds.get('selections', {})[0].get('instances')[0].get('values')[1].get('v'),
                                    odds.get('selections', {})[1].get('instances')[0].get('values')[0].get('v'),
                                    odds.get('selections', {})[1].get('instances')[0].get('values')[1].get('v'),
                                    odds.get('selections', {})[2].get('instances')[0].get('values')[0].get('v'),
                                    odds.get('selections', {})[2].get('instances')[0].get('values')[1].get('v')]],
                                    columns=['rowIndex', 'matchOddsTime', f'{match.awayTeam}_back', f'{match.awayTeam}_lay', f'{match.homeTeam}_back', f'{match.homeTeam}_lay', 'drawBackPrice', 'drawLayPrice'],
                                    ),ignore_index = True)
            
            self.dfToAppend = pd.DataFrame([[match.rowIndex, self.now, 
                                odds.get('selections', {})[0].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[0].get('instances')[0].get('values')[1].get('v'),
                                odds.get('selections', {})[1].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[1].get('instances')[0].get('values')[1].get('v'),
                                odds.get('selections', {})[2].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[2].get('instances')[0].get('values')[1].get('v')]])
                                
            MatchOddsPlusOne.dataframeToCsv(self, match, team) 
            
        marketChanges(self)
        currentMatchOddsPlusOne(self)
    
    
    
    def matchMarketIds(self):
            for market in self.plusOneMarkets:
                for match in matchObjectsList:
                    if market['eventId'] == match.eventId:
                        MatchOddsPlusOne.assignMarketIds(market, match)
                        
    def splitMarketName(market):
        name = market['name'].split(' - ')[1].replace(' +1', '')
        return name
    
    # Assign the market ids of the plus one markets to the 'plusOneToHomeId' and 'plusOneToAwayId' properties in the match object.
    def assignMarketIds(market, match):
        name = MatchOddsPlusOne.splitMarketName(market) 
        if name == match.homeTeam:
            match.plusOneToHomeId = market['id']
            return
        if name == match.awayTeam:
            match.plusOneToAwayId = market['id']
            return
    

    def dataframeToCsv(self, match, team):
        self.dfToAppend.to_csv(f'./plusOneMarkets/{match.fixture}_{team}_plus_one.csv', mode='a', header=False, index=False)        
    
        

class GoalMarkets: 
    
    def __init__(self, eventId):
        self.eventId = eventId
        self.goalMarkets = betAngelApiObject.goalMarkets()
        self.goalMarketsStatusDict = {}
        
        def parse(self):
            for i in self.goalMarkets:
                if i.get('eventId') == eventId:
                    self.goalMarketsStatusDict[f"{i.get('marketType')}"] = i.get('inPlay')
            
        parse(self)

    def goals(self):
        return self.goalMarkets
                    

class BollingerBands:
    
    def __init__(self, eventId, intervals):
        self.eventId = eventId
        self.time = eventId.matchOddsTime
        self.prices = eventId.prices
        self.homePrices = eventId.homeBackPrice
        
        self.rowIndex = eventId.rowIndex
        self.movingAverage = None
        self.oneStandardDev = None
        self.upperStdDev = None
        self.lowerStdDev = None
        ''' CHANGE THIS BACK TO FALSE'''
        if self.eventId.isInPlay == False: 
            return print('Match not yet inplay')

        BollingerBands.loopThroughIntervals(self, eventId, intervals)

    ''' Create Bollingger bands for each time interval in the intervals list'''
    def loopThroughIntervals(self, eventId, intervals):
        self.eventId = eventId
        
        j = 0
        for interval in intervals:
            if interval > self.rowIndex:
                return
            else:
                start = (self.rowIndex)-intervals[j+1]
                end = intervals[j+1]
                
                self.movingAverage = self.eventId.prices['homeBackPrice'].iloc[start:end].mean()
                self.oneStandardDev = self.eventId.prices['homeBackPrice'].iloc[start:end].std(ddof=0)

                # Average of standard deviation
                self.stdAverage = (self.oneStandardDev) + self.movingAverage
                stdAverageNp = np.array(self.stdAverage)            

                # Upper and lower bollinger bands
                self.upperBand = self.movingAverage + 2 * self.oneStandardDev
                self.lowerBand = self.movingAverage - 2 * self.oneStandardDev
                
                # One standard deviation
                self.upperStdDev  = self.movingAverage + 1 * self.oneStandardDev
                self.lowerStdDev = self.movingAverage - 1 * self.oneStandardDev 
   
                self.dfForAppending = pd.DataFrame([[self.rowIndex, self.movingAverage, self.oneStandardDev, self.upperBand, self.lowerBand,self.upperStdDev, self.lowerStdDev]],
                                                    columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])

                BollingerBands.dataframeToCsv(self, intervals[j])
                j += 1
                 
    def dataframeToCsv(self, interval):
        
        self.dfForAppending.to_csv(f'./tempFiles/{self.eventId.fixture}_{interval}.csv', mode='a', header=False, index=False)


class Calculations:
    
    def __init__(self, eventId, intervals):
        self.eventId = eventId
        self.homeXg = eventId.homeXg
        self.awayXg = eventId.awayXg
        self.minOfMatch = math.ceil(eventId.rowIndex / 60)
        self.rowIndex = eventId.rowIndex
        
        self.start = 0
        self.end = 0
        
        self.homeXgForPeriod = None
        self.awayXgForPeriod = None
        
        self.totalLoss = 0
    
    
        def goalCalculations(self, eventId, intervals):
            
            j = 0
            for interval in intervals:
                if interval > self.rowIndex:
                    return print('rowIndex too low for interval:', interval)
                else:

                    self.start = (self.rowIndex)-intervals[j]
                    self.end = intervals[j] + self.start
                    
                    self.pricesPlusOneToHome = eventId.pricesPlusOneToHome
                    self.pricesPlusOneToAway = eventId.pricesPlusOneToAway
                    
                    self.xgsForPeriod = xgForPeriod(self, self.start, self.end)
                    self.plusOneMovingAverages = plusOneMovingAverage(self, self.start, self.end)
                    self.goalPriceMovements = pricesAtPeriodStart(self, self.start)
                    self.h = averageLossHomeLayHomeGoal(self, self.start)
                    self.a = averageGainHomeLayAwayGoal(self, self.start)
                    self.totalLoss = averageLossForPeriodHomeLay(self, self.xgsForPeriod, self.h, self.a)


        def xgForPeriod(self, start, end):
            # Calculate the xg at the start and end of the interval to get the expected goals during that period
            self.homeXgForPeriod = (xGRemaining(self.homeXg, start) - xGRemaining(self.homeXg, end)) / 60
            self.awayXgForPeriod = (xGRemaining(self.awayXg, start) - xGRemaining(self.awayXg, end)) / 60
            return self.homeXgForPeriod, self.awayXgForPeriod
        
        def xGRemaining(xg, minOfMatch):
            return ((1-(1/95*minOfMatch))**.84) * xg
        
        def plusOneMovingAverage(self, start, end):
            
            self.movingAveragePlusOneToHome_homeBack = eventId.pricesPlusOneToHome[f'{eventId.homeTeam}_back'].iloc[start:end].mean()
            self.movingAveragePlusOneToHome_awayBack = eventId.pricesPlusOneToHome[f'{eventId.awayTeam}_back'].iloc[start:end].mean()
            self.movingAveragePlusOneToHome_drawBack = eventId.pricesPlusOneToHome['drawBackPrice'].iloc[start:end].mean()
            
            self.movingAveragePlusOneToHome_homeLay = eventId.pricesPlusOneToHome[f'{eventId.homeTeam}_lay'].iloc[start:end].mean()
            self.movingAveragePlusOneToHome_awayLay = eventId.pricesPlusOneToHome[f'{eventId.awayTeam}_lay'].iloc[start:end].mean()
            self.movingAveragePlusOneToHome_drawLay = eventId.pricesPlusOneToHome['drawLayPrice'].iloc[start:end].mean()
            
            return self.movingAveragePlusOneToHome_homeBack, self.movingAveragePlusOneToHome_awayBack, self.movingAveragePlusOneToHome_drawBack, \
                    self.movingAveragePlusOneToHome_homeLay, self.movingAveragePlusOneToHome_awayLay, self.movingAveragePlusOneToHome_drawLay
        
        def pricesAtPeriodStart(self, start):
            self.homeStartBackPrice = eventId.prices['homeBackPrice'].iloc[start:start+1]
            self.awayStartBackPrice = eventId.prices['awayBackPrice'].iloc[start:start+1]
            self.drawStartBackPrice = eventId.prices['drawBackPrice'].iloc[start:start+1]
            return self.homeStartBackPrice, self.awayStartBackPrice, self.drawStartBackPrice
            
        def averageLossHomeLayHomeGoal(self, start):
            x = eventId.pricesPlusOneToHome.iloc[-1][f'{eventId.homeTeam}_back']-1
            y = eventId.prices.iloc[start-1:start]['homeLayPrice']-1
            z = eventId.pricesPlusOneToHome.iloc[-1][f'{eventId.homeTeam}_back']
            return (x - y) / z
        
        def averageGainHomeLayAwayGoal(self, start):
            x = eventId.pricesPlusOneToAway.iloc[-1][f'{eventId.homeTeam}_back']-1
            y = eventId.prices.iloc[start-1:start]['homeLayPrice']-1
            z = eventId.pricesPlusOneToAway.iloc[-1][f'{eventId.homeTeam}_back']
            return (x - y) / z
            
        def averageLossForPeriodHomeLay(self, xgsForPeriod, h, a):
            return xgsForPeriod[0]*h + xgsForPeriod[1]*a
            
        
        
        goalCalculations(self, eventId, intervals)

  
intervals = [10,300,360,420,480,540,600,660,720,780,840,960,1020,1080,1140,1200]
                
matchObjectsList = matchObjects(betAngelApiObject)

