import requests
from pprint import pprint
import numpy as np
from datetime import datetime, timedelta
import time
import pandas as pd
import math
from statistics import mean

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
        self.isAboutToStart = False # Turns to true if the match is starting within next 5 minutes
        
        self.id = id # Betfair market id
        self.plusOneToHomeId = None
        self.plusOneToAwayId = None
        self.eventId = eventId  # Betfair event id
        self.rapidApiId = None # Rapid Api event id
        
        self.fixture = fixture # Fixture name (formatted)
        self.csFixture = fixture # For getting correct score csv file
        
        self.homeTeam = None # Name of the home team
        self.awayTeam = None # Name of the away team
        self.homeTeamCountry = None # The country where the home team is from
        self.awayTeamCountry = None # The country where the away team is from
        
        self.matchDate = None
        self.startTime = None
        self.dateTimeObject = None
        
        self.isInPlay = isInPlay

        self.matchMinute = 0
        self.timeElapsedOk = False
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
    
        self.prices = pd.DataFrame(columns=['matchOddsTime', 'rowIndex', 'homeBackPrice', 'homeLayPrice', 'awayBackPrice', 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'])

        self.bollingerBandDict = {}

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
            self.bollingerBandDict['10'].to_csv(f'./tempFiles/{self.fixture}_10.csv')
            self.bollingerBandDict['300'].to_csv(f'./tempFiles/{self.fixture}_300.csv')
            self.bollingerBandDict['360'].to_csv(f'./tempFiles/{self.fixture}_360.csv')
            self.bollingerBandDict['420'].to_csv(f'./tempFiles/{self.fixture}_420.csv')
            self.bollingerBandDict['480'].to_csv(f'./tempFiles/{self.fixture}_480.csv')
            self.bollingerBandDict['540'].to_csv(f'./tempFiles/{self.fixture}_540.csv')
            self.bollingerBandDict['600'].to_csv(f'./tempFiles/{self.fixture}_600.csv')
            self.bollingerBandDict['660'].to_csv(f'./tempFiles/{self.fixture}_660.csv')
            self.bollingerBandDict['720'].to_csv(f'./tempFiles/{self.fixture}_720.csv')
            self.bollingerBandDict['780'].to_csv(f'./tempFiles/{self.fixture}_780.csv')
            self.bollingerBandDict['840'].to_csv(f'./tempFiles/{self.fixture}_840.csv')
            self.bollingerBandDict['900'].to_csv(f'./tempFiles/{self.fixture}_900.csv')
            self.bollingerBandDict['960'].to_csv(f'./tempFiles/{self.fixture}_960.csv')
            self.bollingerBandDict['1020'].to_csv(f'./tempFiles/{self.fixture}_1020.csv')
            self.bollingerBandDict['1080'].to_csv(f'./tempFiles/{self.fixture}_1080.csv')
            self.bollingerBandDict['1140'].to_csv(f'./tempFiles/{self.fixture}_1140.csv')
            self.bollingerBandDict['1200'].to_csv(f'./tempFiles/{self.fixture}_1200.csv')
            
        def bollingerBandsDataframeList(self):        
            self.bollingerBandDict = {
                '10':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd']),
                '300':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd']),
                '360':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd']),
                '420':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd']),
                '480':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd']),
                '540':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd']),
                '600':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd']),
                '600':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd']),
                '660':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd']),
                '720':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd']),
                '780':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd']),
                '840':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd']),
                '900':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd']),
                '960':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd']),
                '1020':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd']),
                '1080':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd']),
                '1140':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd']),
                '1200':pd.DataFrame(columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
            }
            return self.bollingerBandDict

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
        bollingerBandsDataframeList(self)
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
    
    def pricesDataframe(self):
        self.prices = (self.prices.groupby(pd.Grouper(key='matchOddsTime', freq='1S')).mean()).round(2)
        return


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
                        MatchPrices.dataframeToCsv(self, match) 

                        break

        def pricesMatchOdds(match, odds):

            self.dfToAppend = pd.DataFrame([[self.now, match.rowIndex, 
                                odds.get('selections', {})[0].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[0].get('instances')[0].get('values')[1].get('v'),
                                odds.get('selections', {})[1].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[1].get('instances')[0].get('values')[1].get('v'),
                                odds.get('selections', {})[2].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[2].get('instances')[0].get('values')[1].get('v')]],
                                columns=['matchOddsTime', 'rowIndex', 'homeBackPrice', 'homeLayPrice', 'awayBackPrice', 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'])

            match.prices = pd.concat([match.prices, self.dfToAppend])
                    
            match.rowIndex += 1
            return 

        currentMatchOdds(self)
           
    def dataframeToCsv(self, match):
        self.dfToAppend.to_csv(f'./tempFiles/{match.fixture}_prices.csv', mode='a', header=False, index=False)
  
              
def matchObjects(betAngelApiObject):
    matchObjectsList = []
    for match in betAngelApiObject.markets():
        if match.get('eventId') == None:
            print('Market is closed')
            continue
        else:
            print(match.get('inPlay'))
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
        
        # self.bollingerBandDict = eventId.bollingerBandDict
        
        self.rowIndex = eventId.rowIndex
        self.movingAverage = None
        self.oneStandardDev = None
        self.upperStdDev = None
        self.lowerStdDev = None
        ''' CHANGE THIS BACK TO FALSE'''
        if self.eventId.isInPlay == False: 
            # return print('Match not yet inplay')
            return None

        BollingerBands.loopThroughIntervals(self, eventId, intervals)

    ''' Create Bollingger bands for each time interval in the intervals list'''
    def loopThroughIntervals(self, eventId, intervals):
        self.eventId = eventId
        
        j = 0
        for interval in intervals:
            if (eventId.prices.iloc[-1:]['matchOddsTime'] - timedelta(seconds=interval)).values[0] - (eventId.prices.iloc[0:1]['matchOddsTime']).values[0] < interval:
                return    
            else:
                start = (eventId.prices.iloc[-1:]['matchOddsTime'] - timedelta(seconds=interval)).values[0]
                end = (eventId.prices.iloc[-1:]['matchOddsTime']).values[0]
                mask = (eventId.prices['matchOddsTime'] >= start) & (eventId.prices['matchOddsTime'] < end)
                sampleDf = eventId.prices.loc[mask].resample('S', on='matchOddsTime')['homeBackPrice', 'homeLayPrice', 'awayBackPrice', 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'].mean()
        
                self.movingAverage = sampleDf['homeBackPrice'].mean()
                self.oneStandardDev = sampleDf['homeBackPrice'].std(ddof=0)
                # print(self.movingAverage)
                
                # Average of standard deviation
                self.stdAverage = (self.oneStandardDev) + self.movingAverage
                # stdAverageNp = np.array(self.stdAverage)            

                # Upper and lower bollinger bands
                self.upperBand = self.movingAverage + 2 * self.oneStandardDev
                self.lowerBand = self.movingAverage - 2 * self.oneStandardDev
                
                # One standard deviation
                self.upperStdDev  = self.movingAverage + 1 * self.oneStandardDev
                self.lowerStdDev = self.movingAverage - 1 * self.oneStandardDev 

                self.dfForAppending = pd.DataFrame([[self.rowIndex, self.movingAverage, self.oneStandardDev, self.upperBand, self.lowerBand,self.upperStdDev, self.lowerStdDev]],
                                                    columns=['rowIndex', 'movingAverage', 'oneStandardDev', 'upperBand', 'lowerBand', 'upperStd', 'lowerStd'])
                
                eventId.bollingerBandDict[f'{str(interval)}'] = eventId.bollingerBandDict[f'{str(interval)}']._append(self.dfForAppending)

                BollingerBands.dataframeToCsv(self, intervals[j])
                j += 1
                 
    def dataframeToCsv(self, interval):
        self.dfForAppending.to_csv(f'./tempFiles/{self.eventId.fixture}_{interval}.csv', mode='a', header=False, index=False)


class Calculations:
    
    def __init__(self, eventId, intervals):
        self.eventId = eventId
        self.homeXg = eventId.homeXg
        self.awayXg = eventId.awayXg
        self.minOfMatchSeconds = math.ceil(eventId.rowIndex)
        self.minOfMatch = math.ceil(eventId.rowIndex / 60)
        self.rowIndex = eventId.rowIndex
        self.interval = None
        
        self.homeXgForPeriod = None
        self.awayXgForPeriod = None
        self.totalLoss = 0
        self.breakEven = self.totalLoss
        
        self.bollingerBandDataframe = None
    
        def goalCalculations(self, eventId, intervals):        
            # Sometimes, when markets are deleted from Bet Angel Guardian, they still appear when the markets are pulled in via the api.
            # This will delete any events that are not in Guardian but appear in the match objects list
            if len(eventId.prices['matchOddsTime']) == 0:
                matchObjectsList.remove(eventId)
                return print('Bet Angel Api thinks market is still loaded in')
            
            for interval in intervals:
                if (eventId.prices.iloc[-1:]['matchOddsTime'] - timedelta(seconds=interval)).values[0] - (eventId.prices.iloc[0:1]['matchOddsTime']).values[0] < interval:
                    return    
                else:
                    matchStartTime = (eventId.prices.iloc[0:1]['matchOddsTime']).values[0]
                    # print(math.ceil(((eventId.prices.iloc[-1:]['matchOddsTime'] - matchStartTime).values[0]).astype('float64')/1e9/60))
                    minOfMatch = math.ceil(((eventId.prices.iloc[-1:]['matchOddsTime'] - matchStartTime).values[0]).astype('float64')/1e9/60)
                    print('min >>>> ', minOfMatch)
                    
                    start = (eventId.prices.iloc[-1:]['matchOddsTime'] - timedelta(seconds=interval)).values[0]
                    end = (eventId.prices.iloc[-1:]['matchOddsTime']).values[0]
                    
                    mask = (eventId.prices['matchOddsTime'] >= start) & (eventId.prices['matchOddsTime'] < end)
                    maskHomePlusOne = (eventId.pricesPlusOneToHome['matchOddsTime'] >= start) & (eventId.pricesPlusOneToHome['matchOddsTime'] < end)
                    maskAwayPlusOne = (eventId.pricesPlusOneToAway['matchOddsTime'] >= start) & (eventId.pricesPlusOneToAway['matchOddsTime'] < end)
                    
                    self.sampleMatchPrices = eventId.prices.loc[mask].resample('S', on='matchOddsTime')['homeBackPrice', 'homeLayPrice', 'awayBackPrice', 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'].mean()
                    self.sampleHomePlusOne = eventId.pricesPlusOneToHome.loc[maskHomePlusOne].resample('S', on='matchOddsTime')[f'{eventId.homeTeam}_back', f'{eventId.homeTeam}_lay', f'{eventId.awayTeam}_back', f'{eventId.awayTeam}_lay', 'drawBackPrice', 'drawLayPrice'].mean()
                    self.sampleAwayPlusOne = eventId.pricesPlusOneToAway.loc[maskAwayPlusOne].resample('S', on='matchOddsTime')[f'{eventId.awayTeam}_back', f'{eventId.awayTeam}_lay', f'{eventId.homeTeam}_back', f'{eventId.homeTeam}_lay', 'drawBackPrice', 'drawLayPrice'].mean()
                    
                    print(self.sampleHomePlusOne)
                    print(eventId.fixture)

                   
                    self.xgsForPeriod = xgForPeriod(self, matchStartTime, end)
                    self.plusOneMovingAverages = plusOneMovingAverage(self, start, end)
                    self.goalPriceMovements = pricesAtPeriodStart(self, start)
                    self.h = averageLossHomeLayHomeGoal(self, start)
                    self.a = averageGainHomeLayAwayGoal(self, start)
                    self.totalLoss = averageLossForPeriodHomeLay(self, self.xgsForPeriod, self.h, self.a).values


                    bollingerBands(self)
                    self.breakEvenPrice = breakEvenCalcs(self)


        def xgForPeriod(self, matchStartTime, end):
            # Calculate the xg at the start and end of the interval to get the expected goals during that period
            self.homeXgForPeriod = (xGRemaining(self.homeXg, self.sampleMatchPrices.iloc[:1]['homeBackPrice'])) - xGRemaining(self.homeXg, self.sampleMatchPrices.iloc[-1:]['homeBackPrice'])
            self.awayXgForPeriod = (xGRemaining(self.awayXg, self.sampleMatchPrices.iloc[:1]['awayBackPrice'])) - xGRemaining(self.awayXg, self.sampleMatchPrices.iloc[-1:]['awayBackPrice'])
            return self.homeXgForPeriod, self.awayXgForPeriod
        
        def xGRemaining(xg, minOfMatch):
            return ((1-((1/95*minOfMatch))**.84) * xg)
        
        def plusOneMovingAverage(self, start, end):
            
            self.movingAveragePlusOneToHome_homeBack = self.sampleHomePlusOne.iloc[0:-1][f'{eventId.homeTeam}_back'].mean()
            self.movingAveragePlusOneToHome_awayBack = self.sampleHomePlusOne.iloc[0:-1][f'{eventId.awayTeam}_back'].mean()
            self.movingAveragePlusOneToHome_drawBack = self.sampleHomePlusOne.iloc[0:-1]['drawBackPrice'].mean()
            
            self.movingAveragePlusOneToHome_homeLay = self.sampleHomePlusOne.iloc[0:-1][f'{eventId.homeTeam}_lay'].mean()
            self.movingAveragePlusOneToHome_awayLay = self.sampleHomePlusOne.iloc[0:-1][f'{eventId.awayTeam}_lay'].mean()
            self.movingAveragePlusOneToHome_drawLay = self.sampleHomePlusOne.iloc[0:-1]['drawLayPrice'].mean()
            
            return self.movingAveragePlusOneToHome_homeBack, self.movingAveragePlusOneToHome_awayBack, self.movingAveragePlusOneToHome_drawBack, \
                    self.movingAveragePlusOneToHome_homeLay, self.movingAveragePlusOneToHome_awayLay, self.movingAveragePlusOneToHome_drawLay
        
        def pricesAtPeriodStart(self, start):
            self.homeStartBackPrice = self.sampleMatchPrices.iloc[0:1]['homeBackPrice']
            self.awayStartBackPrice = self.sampleMatchPrices.iloc[0:1]['awayBackPrice']
            self.drawStartBackPrice = self.sampleMatchPrices.iloc[0:1]['drawBackPrice']
            return self.homeStartBackPrice, self.awayStartBackPrice, self.drawStartBackPrice
            
        def averageLossHomeLayHomeGoal(self, start):
            x = eventId.pricesPlusOneToHome.iloc[-1][f'{eventId.homeTeam}_back']-1
            y = eventId.sampleMatchPrices['homeLayPrice']-1
            z = eventId.pricesPlusOneToHome.iloc[-1][f'{eventId.homeTeam}_back']
            return (x - y) / z
        
        def averageGainHomeLayAwayGoal(self, start):
            x = eventId.pricesPlusOneToAway.iloc[-1][f'{eventId.homeTeam}_back']-1
            y = eventId.prices.iloc[start:start+1]['homeLayPrice']-1
            z = eventId.pricesPlusOneToAway.iloc[-1][f'{eventId.homeTeam}_back']
            return (x - y) / z
            
        def averageLossForPeriodHomeLay(self, xgsForPeriod, h, a):
            # print('~~~~~~~~~~~~~~~~~~~~')
            # print(xgsForPeriod[0], '\n', xgsForPeriod[1], '\n', h, '\n', a, '\n')
            # print('~~~~~~~~~~~~~~~~~~~~')
            return xgsForPeriod[0]*h + xgsForPeriod[1]*a
        
        def bollingerBands(self):
            self.bollingerBandDataframe = eventId.bollingerBandDict[f'{str(self.interval)}']
            return self.bollingerBandDataframe
        
        def breakEvenCalcs(self):         
            self.breakEven = self.totalLoss
            self.price = eventId.prices.iloc[self.start]['homeBackPrice']
            self.initialPrice = eventId.prices.iloc[self.start]['homeBackPrice'] # Price at the start of the interval

            while self.breakEven < 0:
                self.price += 0.01 / 60
                self.breakEven = self.breakEven + (((self.price-1) - (self.initialPrice-1)) / self.price)
                # print(self.breakEven, self.price, self.start, self.end)
            return self.price
                
        def placeBetCalcs(self):
            if self.homeBackAverage - self.price < 0:
                return False
            
            if self.homeBackAverage - self.price >= 0:
                ''' Change this to '-60' '''
                self.homeBackAverage = mean(self.eventId.prices.iloc[self.minOfMatchSeconds-10: self.minOfMatchSeconds]['homeBackPrice']) # Average price over the last 60 seconds
                self.awayBackAverage = mean(self.eventId.prices.iloc[self.minOfMatchSeconds-10: self.minOfMatchSeconds]['awayBackPrice']) # Average price over the last 60 seconds
                
                
            
            return
        
        def priceSpikes(self, homeBackAverage, awayBackAverage):   
            rangeValue = 10
            
            if self.interval < 600:
                rangeValue = int(self.interval)       
            for s in range(self.rowIndex - rangeValue, rangeValue):
                spikeTest = homeBackAverage * 0.85
                if spikeTest > eventId.prices.iloc[self.rowIndex-1-s:self.rowIndex-s]['homeBackPrice'].values or spikeTest > eventId.prices.iloc[5]['homeBackPrice']:
                    return False
                if eventId.prices.iloc[self.rowIndex-1-s:self.rowIndex-s]['homeBackPrice'].values < self.bollingerBandDataframe.iloc[0:1]['movingAverage'].values:
                    return False
            return True
            
        def rateOfChange(self, totalLoss):
                   
            return
            
        goalCalculations(self, eventId, intervals)
        

intervals = [10,300,360,420,480,540,600,660,720,780,840,960,1020,1080,1140,1200]            
matchObjectsList = matchObjects(betAngelApiObject)

