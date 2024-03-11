import requests
from pprint import pprint
import numpy as np
from datetime import datetime, timedelta
import time
import pandas as pd
import csv
import os

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
   
        self.pricesPlusOneToHome = pd.DataFrame(columns=['rowIndex', 'matchOddsTime', 'homeBackPrice', 'homeLayPrice', 'awayBackPrice', 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'])
        self.pricesPlusOneToAway = pd.DataFrame(columns=['rowIndex', 'matchOddsTime', 'homeBackPrice', 'homeLayPrice', 'awayBackPrice', 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'])
   
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
        
        self.bollingerList = [self.bollingerBands10]

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

        fixtureParse(self, fixture)
        dateAndTime(self, dateTimeString)
        matchDateTime(self, dateTimeString)
        teams(self, selections)
        teamsCountry(self)
        createCsvs(self)
       
         
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

    def __init__(self):
        self.latestOdds = betAngelApiObject.marketPrices()
        self.latestOddsPlusOne = betAngelApiObject.plusOneMarkets()
        self.marketLatestOdds = None
        
        ''' Check if the market has finished and is now closed'''
        def currentMatchOdds(self):
            for odds in self.latestOdds:
                for match in matchObjectsList:
                    if match.id == odds.get('id') and odds.get('status') != 'CLOSED': 
                        pricesMatchOdds(match, odds) 
                        if checkForTimeGaps(match) != 0:           
                             break
                        break
                    
        def currentMatchOddsPlusOne(self):
            for odds in self.latestOddsPlusOne:
                for match in matchObjectsList:
                    if match.id == odds.get('id') and odds.get('status') != 'CLOSED': 
                        pricesPlusOneMatchOdds(match, odds) 
                        if checkForTimeGapsPlusOne(match) != 0:           
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
            
        def checkForTimeGapsPlusOne(match):
            self.prices = match.prices
            self.eventId = match.eventId

            # if len(match.prices['matchOddsTime']) == 0:
            #     matchObjectsList.remove(match.eventId)
            #     return print('Bet Angel Api thinks market is still loaded in')
          
            self.startTime = match.prices['matchOddsTime'][0]
            self.currentTime = match.prices.iloc[-1, 1]
            
            if match.rowIndex - (self.currentTime - self.startTime).total_seconds() != 1:
                MatchPrices.changeTimeData(self, match)
                print('Time is corrupted', match.rowIndex - (self.currentTime - self.startTime).total_seconds(), self.startTime, self.currentTime, match.rowIndex, self.eventId.matchOddsTime[self.eventId.rowIndex-1][0])
                return 0
        
        def pricesMatchOdds(match, odds):
            
            now = datetime.now().replace(microsecond=0) # Use the time now as the timestamp

            match.prices = match.prices._append(pd.DataFrame([[match.rowIndex, now, 
                                odds.get('selections', {})[0].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[0].get('instances')[0].get('values')[1].get('v'),
                                odds.get('selections', {})[1].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[1].get('instances')[0].get('values')[1].get('v'),
                                odds.get('selections', {})[2].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[2].get('instances')[0].get('values')[1].get('v')]],
                                columns=['rowIndex', 'matchOddsTime', 'homeBackPrice', 'homeLayPrice', 'awayBackPrice', 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'],
                                ),ignore_index = True)      
            
            self.dfToAppend = pd.DataFrame([[match.rowIndex, now, 
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
        
        def pricesPlusOneMatchOdds(self):
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
    
    def __init__(self):
        self.latestOdds = betAngelApiObject.plusOneMarkets()
        
        def matchMarketIds(self):
            for market in self.latestOdds:
                for match in matchObjectsList:
                    if market['eventId'] == match.eventId:
                        assignMarketIds(market, match)
                        
        def splitMarketName(market):
            name = market['name'].split(' - ')[1].replace(' +1', '')
            return name
            
        def assignMarketIds(market, match):
            name = splitMarketName(market) 
            if name == match.homeTeam:
                match.plusOneToHomeId = market['id']
                return
            if name == match.awayTeam:
                match.plusOneToAwayId = market['id']
                return
            
            
        matchMarketIds(self)
        
        
        


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

        if self.eventId.isInPlay == False:
            return

        BollingerBands.loopThroughIntervals(self, eventId, intervals)


    def loopThroughIntervals(self, eventId, intervals):
        self.eventId = eventId
        bollingerList = eventId.bollingerList
        
        j = 0
        for interval in intervals:
            self.eventId.bollingerListItem = bollingerList[0]
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



    

  
intervals = [10,300,360,420,480,540,600,660,720,780,840,960,1020,1080,1160,1200] 
                
matchObjectsList = matchObjects(betAngelApiObject)

