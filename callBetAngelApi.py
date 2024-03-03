import requests
from pprint import pprint
import numpy as np
from datetime import datetime


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
    
    
    def goalMarkets(self):
        endpoint = "getMarkets"      
        dataRequired = '{"dataRequired":["ID","MARKET_INPLAY_STATUS","EVENT_ID","MARKET_TYPE"]}' 
        return CallBetfair.request(endpoint, dataRequired, self.goalMarketsPort, 'markets').get('result',{}).get('markets')
    
    def __repr__(self):
        return self.markets


def createBetAngelApiObject(): 
    callBetfairObject = CallBetfair(9000,9001,9002,9003)
    return callBetfairObject

betAngelApiObject = createBetAngelApiObject()


class Match:
    
    def __init__(self, id, eventId, fixture, dateTimeString, selections, isInPlay):
        
        self.rowIndex = 0
        self.inplayRowIndex = 0
        self.isAboutToStart = False
        
        self.id = id
        self.eventId = eventId 
        self.fixture = fixture
        self.homeTeam = None
        self.awayTeam = None 
        self.matchDate = None
        self.startTime = None
        self.isInPlay = isInPlay
        self.matchScore = (0,0)
        self.matchMinute = 0
        
        self.matchOddsTime = np.ndarray(shape=(18000, 1), dtype='U33')

        self.matchOdds = np.ndarray(shape=(18000), 
                                    dtype=[('homeBack', 'float'),('homeLay', 'float'),('awayBack', 'float'),
                                            ('awayLay', 'float'),('drawBack', 'float'),('drawLay', 'float')])

        def fixtureParse(self, fixture):
            self.fixture = (fixture.split(' - '))[0]
            return self.fixture
        
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

        fixtureParse(self, fixture)
        dateAndTime(self, dateTimeString)
        teams(self, selections)
        
    def __repr__(self):
        return self.eventId
        
    def inPlayStatus(self, isInPlay):
        self.isInPlay = isInPlay
        
    def date(self):
        return self.matchDate
    
    def score(self):
        return self.matchScore
    
    def minute(self):
        return self.matchMinute


class MatchPrices():

    def __init__(self):
        self.latestOdds = betAngelApiObject.marketPrices()
        self.rowIndex = 0
        self.marketLatestOdds = None
    
        def currentMatchOdds(self):
            for odds in self.latestOdds:
                for match in matchObjectsList:
                    if match.id == odds.get('id') and odds.get('status') != 'CLOSED':
                        updateMatchOdds(match, odds)  
                        break

        def updateMatchOdds(match, odds):
            
            start = match.rowIndex
            end = match.rowIndex+1
            now = datetime.now().time().replace(microsecond=0) # Use the time now as the timestamp
            
            # When start == 0, match.matchOddsTime[start-1] == match.matchOddsTime[17999]
            if match.matchOddsTime[start-1] == str(now):
                return
            else:   
                # Update the Match instance prices  
                match.matchOddsTime[start:end] = now
                
                match.matchOdds['homeBack'][start:end] = odds.get('selections', {})[0].get('instances')[0].get('values')[0].get('v') # home team back price
                match.matchOdds['homeLay'][start:end] = odds.get('selections', {})[0].get('instances')[0].get('values')[1].get('v') # home team lay price
                
                match.matchOdds['awayBack'][start:end] = odds.get('selections', {})[1].get('instances')[0].get('values')[0].get('v') # away team back price
                match.matchOdds['awayLay'][start:end] = odds.get('selections', {})[1].get('instances')[0].get('values')[1].get('v') # away team lay price
                
                match.matchOdds['drawBack'][start:end] = odds.get('selections', {})[2].get('instances')[0].get('values')[0].get('v') # draw back price
                match.matchOdds['drawLay'][start:end] = odds.get('selections', {})[2].get('instances')[0].get('values')[1].get('v') # draw lay price


                print(now, '', (match.matchOdds[0:10]), (match.matchOddsTime[0:10]))

                
                match.rowIndex += 1
            
                return 
  
        
        currentMatchOdds(self)
           

def matchObjects(betAngelApiObject):
    matchObjectsList = []
    for match in betAngelApiObject.markets():
        if match.get('eventId') == None:
            print('Market is closed')
            continue
        else:
            matchObjectsList.append(Match(match.get('id'), match.get('eventId'), match.get('name'), match.get('startTime'), match.get('selections'), match.get('inPlay')))
    return matchObjectsList


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
                    
    

    
matchObjectsList = matchObjects(betAngelApiObject)
i = 0
while i < 1:
    # time.sleep(1)
    x = MatchPrices()
    i += 1
    



def placeBackBet():
    return