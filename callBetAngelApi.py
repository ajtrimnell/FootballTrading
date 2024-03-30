# from datetime import timedelta
# import pandas as pd
# import math

# # from teamsCountries import *
# from betting import *
# from main import betAngelApiObject
# from matchPrices import MatchPrices, MatchOddsPlusOne

# from callBetfair import CallBetfair
# from match import Match

# def createBetAngelApiObject(): 
#     ''' 
#     Ports:
#     9000 - Match odds
#     9001 - Match odds +1
#     9002 - Correct score - Currently getting the xg from a csv, so this redundant
#     9003 - Goal markets
#     '''
#     callBetfairObject = CallBetfair(9000,9001,9002,9003)
#     return callBetfairObject

# ''' Create an object that will be used for all api calls. This means that only one object is created daily '''
# betAngelApiObject = createBetAngelApiObject()


# class Match:
    
#     def __init__(self, id, eventId, fixture, dateTimeString, selections, isInPlay):
        
#         self.rowIndex = 0
#         self.isAboutToStart = False # Turns to true if the match is starting within next 5 minutes
        
#         self.id = id # Betfair market id
#         self.plusOneToHomeId = None
#         self.plusOneToAwayId = None
#         self.eventId = eventId  # Betfair event id
#         self.rapidApiId = None # Rapid Api event id
        
#         self.fixture = fixture # Fixture name (formatted)
#         self.csFixture = fixture # For getting correct score csv file
        
#         self.homeTeam = None # Name of the home team
#         self.awayTeam = None # Name of the away team
#         self.homeTeamCountry = None # The country where the home team is from
#         self.awayTeamCountry = None # The country where the away team is from
        
#         self.homeBetfairId = None
#         self.awayBetfairId = None
#         self.drawBetfairId = None
        
#         self.matchDate = None
#         self.startTime = None
#         self.dateTimeObject = None
        
#         self.isInPlay = isInPlay

#         self.matchMinute = 0
#         self.timeElapsedOk = False
#         self.matchScore = (0,0)
#         self.homeGoals = None
#         self.awayGoals = None
         
#         self.homeXg = None
#         self.awayXg = None
        
#         self.matchOddsTime = np.ndarray(shape=(9000, 1), dtype='U33')

#         self.homeBackPrice = np.ndarray(shape=(9000), 
#                                         dtype= 'float')
#         self.homeLayPrice = np.ndarray(shape=(9000), 
#                                         dtype= 'float')
#         self.awayBackPrice = np.ndarray(shape=(9000), 
#                                         dtype= 'float')
#         self.awayLayPrice = np.ndarray(shape=(9000), 
#                                         dtype= 'float')
#         self.drawBackPrice = np.ndarray(shape=(9000), 
#                                         dtype= 'float')
#         self.drawLayPrice = np.ndarray(shape=(9000), 
#                                         dtype= 'float')
    
#         self.prices = pd.DataFrame(columns=['matchOddsTime', 'rowIndex', 'homeBackPrice', 'homeLayPrice', 'awayBackPrice', 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'])

#         self.bollingerBandDict = {}

#         self.betPlaced = False
#         self.positionExited = False
        
#         ''' Betting '''
#         self.numberOfBetsPlaced = 0

#         def fixtureParse(self, fixture):
#             self.fixture = (fixture.split(' - '))[0]
#             self.csFixture = self.fixture + ' - ' + 'Correct Score'
#             self.fixture = self.fixture.replace(' v ', '_v_')
#             return self.fixture, self.csFixture
        
#         def matchDateTime(self, dateTimeString):
#             self.dateTimeObject = datetime.strptime(dateTimeString.replace('T', ' ').replace('+00:00', ''), '%Y-%m-%d %H:%M:%S')
#             return self.dateTimeObject         
        
#         def dateAndTime(self, dateTimeString):
#             self.matchDate = (dateTimeString.split('T'))[0]
#             self.startTime = ((dateTimeString.split('T'))[1].split('+'))[0]
#             return self.matchDate, self.startTime

#         def teams(self, selections):
#             self.homeBetfairId = selections[0].get('id')
#             self.homeTeam = selections[0].get('name')
#             self.awayId = selections[1].get('id')
#             self.awayTeam = selections[1].get('name')
#             self.drawBetfairId = selections[2].get('id')
#             return self.homeBetfairId, self.homeTeam, self.awayBetfairId, self.awayTeam, self.drawBetfairId
        
#         def teamsCountry(self):
#             self.homeTeamCountry = countries[self.homeTeam]
#             self.awayTeamCountry = countries[self.awayTeam]

#         def createCsvs(self):
#             self.prices.to_csv(f'./tempFiles/{self.fixture}_prices.csv')
#             self.bollingerBandDict['10'].to_csv(f'./tempFiles/{self.fixture}_10.csv')
#             self.bollingerBandDict['300'].to_csv(f'./tempFiles/{self.fixture}_300.csv')
#             self.bollingerBandDict['360'].to_csv(f'./tempFiles/{self.fixture}_360.csv')
#             self.bollingerBandDict['420'].to_csv(f'./tempFiles/{self.fixture}_420.csv')
#             self.bollingerBandDict['480'].to_csv(f'./tempFiles/{self.fixture}_480.csv')
#             self.bollingerBandDict['540'].to_csv(f'./tempFiles/{self.fixture}_540.csv')
#             self.bollingerBandDict['600'].to_csv(f'./tempFiles/{self.fixture}_600.csv')
#             self.bollingerBandDict['660'].to_csv(f'./tempFiles/{self.fixture}_660.csv')
#             self.bollingerBandDict['720'].to_csv(f'./tempFiles/{self.fixture}_720.csv')
#             self.bollingerBandDict['780'].to_csv(f'./tempFiles/{self.fixture}_780.csv')
#             self.bollingerBandDict['840'].to_csv(f'./tempFiles/{self.fixture}_840.csv')
#             self.bollingerBandDict['900'].to_csv(f'./tempFiles/{self.fixture}_900.csv')
#             self.bollingerBandDict['960'].to_csv(f'./tempFiles/{self.fixture}_960.csv')
#             self.bollingerBandDict['1020'].to_csv(f'./tempFiles/{self.fixture}_1020.csv')
#             self.bollingerBandDict['1080'].to_csv(f'./tempFiles/{self.fixture}_1080.csv')
#             self.bollingerBandDict['1140'].to_csv(f'./tempFiles/{self.fixture}_1140.csv')
#             self.bollingerBandDict['1200'].to_csv(f'./tempFiles/{self.fixture}_1200.csv')
            
#         def bollingerBandsDataframeDict(self):        
#             self.bollingerBandDict = {
#                 '10':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#                 '300':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#                 '360':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#                 '420':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#                 '480':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#                 '540':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#                 '600':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#                 '600':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#                 '660':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#                 '720':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#                 '780':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#                 '840':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#                 '900':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#                 '960':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#                 '1020':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#                 '1080':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#                 '1140':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#                 '1200':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                            'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
#             }
#             return self.bollingerBandDict

#         def plusOneCsvs(self):
#             self.pricesPlusOneToHome.to_csv(f'./plusOneMarkets/{self.fixture}_{self.homeTeam}_plus_one.csv')
#             self.pricesPlusOneToAway.to_csv(f'./plusOneMarkets/{self.fixture}_{self.awayTeam}_plus_one.csv')

#         def plusOneDataframes(self):
#             self.pricesPlusOneToHome = pd.DataFrame(columns=['rowIndex', 'matchOddsTime', f'{self.homeTeam}_back', f'{self.homeTeam}_lay', f'{self.awayTeam}_back', f'{self.awayTeam}_lay', 'drawBackPrice', 'drawLayPrice'])
#             self.pricesPlusOneToAway = pd.DataFrame(columns=['rowIndex', 'matchOddsTime', f'{self.awayTeam}_back', f'{self.awayTeam}_lay', f'{self.homeTeam}_back', f'{self.homeTeam}_lay', 'drawBackPrice', 'drawLayPrice'])
            
#         fixtureParse(self, fixture)
#         dateAndTime(self, dateTimeString)
#         matchDateTime(self, dateTimeString)
#         teams(self, selections)
#         teamsCountry(self)
#         bollingerBandsDataframeDict(self)
#         createCsvs(self)
#         plusOneDataframes(self)
#         plusOneCsvs(self)
        
#     def __repr__(self):
#         return self.eventId
          
#     def getXg(self):
#         try:
#             file = open(f'./xgFiles/_{self.csFixture}.csv', mode='r')
#         except FileNotFoundError:
#             return print(f'{self.csFixture} file not found')
        
#         content = file.read().split('\n')
#         content[1] = content[1].split(',')

#         self.homeXg = round(float(content[1][8]), 2)
#         self.awayXg = round(float(content[1][6]), 2)
#         return self.homeXg, self.awayXg
    
#     def pricesDataframe(self):
#         self.prices = (self.prices.groupby(pd.Grouper(key='matchOddsTime', freq='1S')).mean()).round(2)
#         return


# class MatchPrices:

#     def __init__(self, now):
#         self.latestOdds = betAngelApiObject.marketPrices()
#         self.marketLatestOdds = None
#         self.now = now
             
#         ''' Check if the market has finished and is now closed'''
#         def currentMatchOdds(self):
#             for odds in self.latestOdds:
#                 for match in matchObjectsList:
#                     if match.id == odds.get('id') and odds.get('status') != 'CLOSED': 
#                         pricesMatchOdds(match, odds)
#                         MatchPrices.dataframeToCsv(self, match) 

#                         break

#         def pricesMatchOdds(match, odds):

#             self.dfToAppend = pd.DataFrame([[self.now, match.rowIndex, 
#                                 odds.get('selections', {})[0].get('instances')[0].get('values')[0].get('v'),
#                                 odds.get('selections', {})[0].get('instances')[0].get('values')[1].get('v'),
#                                 odds.get('selections', {})[1].get('instances')[0].get('values')[0].get('v'),
#                                 odds.get('selections', {})[1].get('instances')[0].get('values')[1].get('v'),
#                                 odds.get('selections', {})[2].get('instances')[0].get('values')[0].get('v'),
#                                 odds.get('selections', {})[2].get('instances')[0].get('values')[1].get('v')]],
#                                 columns=['matchOddsTime', 'rowIndex', 'homeBackPrice', 'homeLayPrice', 'awayBackPrice', 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'])

#             match.prices = pd.concat([match.prices, self.dfToAppend])
                    
#             match.rowIndex += 1
#             return 

#         currentMatchOdds(self)
           
#     def dataframeToCsv(self, match):
#         self.dfToAppend.to_csv(f'./tempFiles/{match.fixture}_prices.csv', mode='a', header=False, index=False)
  
              
# def matchObjects(betAngelApiObject):
#     matchObjectsList = []
#     for match in betAngelApiObject.markets():
#         if match.get('eventId') == None:
#             print('Market is closed')
#             continue
#         else:
#             print(match.get('inPlay'))
#             matchObjectsList.append(Match(match.get('id'), match.get('eventId'), match.get('name'), match.get('startTime'), match.get('selections'), match.get('inPlay')))
#     return matchObjectsList


# class MatchOddsPlusOne:
    
#     def __init__(self, now):
#         self.plusOneMarkets = betAngelApiObject.plusOneMarkets()
#         self.latestOddsPlusOne = betAngelApiObject.plusOneMarketPrices()
#         self.now = now
        
#         def marketChanges(self):
#             for match in matchObjectsList:
#                 if match.plusOneToHomeId == None and match.plusOneToHomeId == None:
#                     MatchOddsPlusOne.matchMarketIds(self)
        
#         def currentMatchOddsPlusOne(self):
#             for odds in self.latestOddsPlusOne:
#                 for match in matchObjectsList:
#                     if match.plusOneToHomeId == odds.get('id') and odds.get('status') != 'CLOSED': 
#                         pricesHomeTeamPlusOne(match, odds, match.homeTeam)
#                         break
#                     if match.plusOneToAwayId == odds.get('id') and odds.get('status') != 'CLOSED': 
#                         pricesAwayTeamPlusOne(match, odds, match.awayTeam)
#                         break        
        
#         def pricesHomeTeamPlusOne(match, odds, homeTeam):
#             dataframeToAppend(match, odds, homeTeam)
#             return
        
#         def pricesAwayTeamPlusOne(match, odds, AwayTeam):
#             dataframeToAppend(match, odds, AwayTeam)
#             return
        
#         def dataframeToAppend(match, odds, team):
#             if team == match.homeTeam:
#                 match.pricesPlusOneToHome = match.pricesPlusOneToHome._append(pd.DataFrame([[match.rowIndex, self.now, 
#                                     odds.get('selections', {})[0].get('instances')[0].get('values')[0].get('v'),
#                                     odds.get('selections', {})[0].get('instances')[0].get('values')[1].get('v'),
#                                     odds.get('selections', {})[1].get('instances')[0].get('values')[0].get('v'),
#                                     odds.get('selections', {})[1].get('instances')[0].get('values')[1].get('v'),
#                                     odds.get('selections', {})[2].get('instances')[0].get('values')[0].get('v'),
#                                     odds.get('selections', {})[2].get('instances')[0].get('values')[1].get('v')]],
#                                     columns=['rowIndex', 'matchOddsTime', f'{match.homeTeam}_back', f'{match.homeTeam}_lay', f'{match.awayTeam}_back', f'{match.awayTeam}_lay', 'drawBackPrice', 'drawLayPrice'],
#                                     ),ignore_index = True)
#             else:
#                 match.pricesPlusOneToAway = match.pricesPlusOneToAway._append(pd.DataFrame([[match.rowIndex, self.now, 
#                                     odds.get('selections', {})[0].get('instances')[0].get('values')[0].get('v'),
#                                     odds.get('selections', {})[0].get('instances')[0].get('values')[1].get('v'),
#                                     odds.get('selections', {})[1].get('instances')[0].get('values')[0].get('v'),
#                                     odds.get('selections', {})[1].get('instances')[0].get('values')[1].get('v'),
#                                     odds.get('selections', {})[2].get('instances')[0].get('values')[0].get('v'),
#                                     odds.get('selections', {})[2].get('instances')[0].get('values')[1].get('v')]],
#                                     columns=['rowIndex', 'matchOddsTime', f'{match.awayTeam}_back', f'{match.awayTeam}_lay', f'{match.homeTeam}_back', f'{match.homeTeam}_lay', 'drawBackPrice', 'drawLayPrice'],
#                                     ),ignore_index = True)
            
#             self.dfToAppend = pd.DataFrame([[match.rowIndex, self.now, 
#                                 odds.get('selections', {})[0].get('instances')[0].get('values')[0].get('v'),
#                                 odds.get('selections', {})[0].get('instances')[0].get('values')[1].get('v'),
#                                 odds.get('selections', {})[1].get('instances')[0].get('values')[0].get('v'),
#                                 odds.get('selections', {})[1].get('instances')[0].get('values')[1].get('v'),
#                                 odds.get('selections', {})[2].get('instances')[0].get('values')[0].get('v'),
#                                 odds.get('selections', {})[2].get('instances')[0].get('values')[1].get('v')]])
                                
#             MatchOddsPlusOne.dataframeToCsv(self, match, team) 
            
#         marketChanges(self)
#         currentMatchOddsPlusOne(self)
    
#     def matchMarketIds(self):
#             for market in self.plusOneMarkets:
#                 for match in matchObjectsList:
#                     if market['eventId'] == match.eventId:
#                         MatchOddsPlusOne.assignMarketIds(market, match)
                        
#     def splitMarketName(market):
#         name = market['name'].split(' - ')[1].replace(' +1', '')
#         return name
    
#     # Assign the market ids of the plus one markets to the 'plusOneToHomeId' and 'plusOneToAwayId' properties in the match object.
#     def assignMarketIds(market, match):
#         name = MatchOddsPlusOne.splitMarketName(market) 
#         if name == match.homeTeam:
#             match.plusOneToHomeId = market['id']
#             return
#         if name == match.awayTeam:
#             match.plusOneToAwayId = market['id']
#             return
    
#     def dataframeToCsv(self, match, team):
#         self.dfToAppend.to_csv(f'./plusOneMarkets/{match.fixture}_{team}_plus_one.csv', mode='a', header=False, index=False)        
    
        
# class GoalMarkets: 
    
#     def __init__(self, eventId):
#         self.eventId = eventId
#         self.goalMarkets = betAngelApiObject.goalMarkets()
#         self.goalMarketsStatusDict = {}
        
#         def parse(self):
#             for i in self.goalMarkets:
#                 if i.get('eventId') == eventId:
#                     self.goalMarketsStatusDict[f"{i.get('marketType')}"] = i.get('inPlay')
            
#         parse(self)

#     def goals(self):
#         return self.goalMarkets
                    

# class BollingerBands:
    
#     def __init__(self, eventId, intervals):
#         self.eventId = eventId
#         self.time = eventId.matchOddsTime
        
#         self.prices = eventId.prices
#         self.homePrices = eventId.homeBackPrice
#         self.awayPrices = eventId.awayBackPrice

#         self.rowIndex = eventId.rowIndex
        
#         self.homeMovingAverage = None
#         self.homeOneStandardDev = None
#         self.homeUpperStdDev = None
#         self.homeLowerStdDev = None
        
#         self.awayMovingAverage = None
#         self.awayOneStandardDev = None
#         self.awayUpperStdDev = None
#         self.awayLowerStdDev = None
        
#         ''' CHANGE THIS BACK TO FALSE'''
#         # if self.eventId.isInPlay == False: 
#         #     # return print('Match not yet inplay')
#         #     return None

#         BollingerBands.loopThroughIntervals(self, eventId, intervals)

#     ''' Create Bollingger bands for each time interval in the intervals list'''
#     def loopThroughIntervals(self, eventId, intervals):
#         self.eventId = eventId
#         # print(self.prices)
#         j = 0
#         for interval in intervals:
#             if (eventId.prices.iloc[-1:]['matchOddsTime'] - timedelta(seconds=interval)).values[0] - (eventId.prices.iloc[0:1]['matchOddsTime']).values[0] < interval:
#                 return    
#             else:
#                 start = (eventId.prices.iloc[-1:]['matchOddsTime'] - timedelta(seconds=interval)).values[0]
#                 end = (eventId.prices.iloc[-1:]['matchOddsTime']).values[0]
#                 mask = (eventId.prices['matchOddsTime'] >= start) & (eventId.prices['matchOddsTime'] < end)
#                 self.sampleDf = eventId.prices.loc[mask].resample('S', on='matchOddsTime')['homeBackPrice', 'homeLayPrice', 'awayBackPrice', 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'].mean()

#                 self.homeMovingAverage = self.sampleDf['homeBackPrice'].mean()
#                 self.homeOneStandardDev = self.sampleDf['homeBackPrice'].std(ddof=0)
#                 self.awayMovingAverage = self.sampleDf['awayBackPrice'].mean()
#                 self.awayOneStandardDev = self.sampleDf['awayBackPrice'].std(ddof=0)

#                 # Average of standard deviation
#                 self.homeStdAverage = (self.homeOneStandardDev) + self.homeMovingAverage   
#                 self.awayStdAverage = (self.awayOneStandardDev) + self.awayMovingAverage    

#                 # Upper and lower bollinger bands
#                 self.homeUpperBand = self.homeMovingAverage + 2 * self.homeOneStandardDev
#                 self.homeLowerBand = self.homeMovingAverage - 2 * self.homeOneStandardDev
#                 self.awayUpperBand = self.awayMovingAverage + 2 * self.awayOneStandardDev
#                 self.awayLowerBand = self.awayMovingAverage - 2 * self.awayOneStandardDev
                
#                 # One standard deviation
#                 self.homeUpperStdDev  = self.homeMovingAverage + 1 * self.homeOneStandardDev
#                 self.homeLowerStdDev = self.homeMovingAverage - 1 * self.homeOneStandardDev 
#                 self.awayUpperStdDev  = self.awayMovingAverage + 1 * self.awayOneStandardDev
#                 self.awayLowerStdDev = self.awayMovingAverage - 1 * self.awayOneStandardDev 

#                 self.dfForAppending = pd.DataFrame([[self.rowIndex, end, self.homeMovingAverage, self.homeOneStandardDev, self.homeUpperBand, self.homeLowerBand,self.homeUpperStdDev, self.homeLowerStdDev, 
#                                                      self.awayMovingAverage, self.awayOneStandardDev, self.awayUpperBand, self.awayLowerBand, self.awayUpperStdDev, self.awayLowerStdDev]],
#                                                     columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
#                                                              'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd'])

#                 eventId.bollingerBandDict[f'{str(interval)}'] = eventId.bollingerBandDict[f'{str(interval)}']._append(self.dfForAppending)

#                 BollingerBands.dataframeToCsv(self, intervals[j])
#                 j += 1
                 
#     def dataframeToCsv(self, interval):
#         self.dfForAppending.to_csv(f'./tempFiles/{self.eventId.fixture}_{interval}.csv', mode='a', header=False, index=False)


# class Calculations:
    
#     def __init__(self, eventId, intervals):
#         self.eventId = eventId
#         self.homeXg = eventId.homeXg
#         self.awayXg = eventId.awayXg
#         self.minOfMatchSeconds = math.ceil(eventId.rowIndex)
#         self.minOfMatch = math.ceil(eventId.rowIndex / 60)
#         self.rowIndex = eventId.rowIndex
#         self.interval = None
        
#         self.homeXgForPeriod = None
#         self.awayXgForPeriod = None
    
#         def goalCalculations(self, eventId, intervals):        
#             # Sometimes, when markets are deleted from Bet Angel Guardian, they still appear when the markets are pulled in via the api.
#             # This will delete any events that are not in Guardian but appear in the match objects list
#             if len(eventId.prices['matchOddsTime']) == 0:
#                 # matchObjectsList.remove(eventId)
#                 return ['Bet Angel Api thinks market is still loaded in', 0]
            
#             for interval in intervals:
#                 self.interval = interval
#                 if (eventId.prices.iloc[-1:]['matchOddsTime'] - timedelta(seconds=interval)).values[0] - (eventId.prices.iloc[0:1]['matchOddsTime']).values[0] < interval:
#                     return    
#                 else:
#                     matchStartTime = (eventId.prices.iloc[0:1]['matchOddsTime']).values[0]

#                     self.minOfMatch = math.ceil(((eventId.prices.iloc[-1:]['matchOddsTime'] - matchStartTime).values[0]).astype('float64')/1e9/60)
#                     self.start = (eventId.prices.iloc[-1:]['matchOddsTime'] - timedelta(seconds=interval)).values[0]
#                     self.end = (eventId.prices.iloc[-1:]['matchOddsTime']).values[0]
                    
#                     self.mask = (eventId.prices['matchOddsTime'] >= self.start) & (eventId.prices['matchOddsTime'] < self.end)
#                     self.bollingerMask = (eventId.bollingerBandDict[f'{str(self.interval)}']['matchTime'] >= self.start) & (eventId.bollingerBandDict[f'{str(self.interval)}']['matchTime'] < self.end)
#                     self.maskHomePlusOne = (eventId.pricesPlusOneToHome['matchOddsTime'] >= self.start) & (eventId.pricesPlusOneToHome['matchOddsTime'] < self.end)
#                     self.maskAwayPlusOne = (eventId.pricesPlusOneToAway['matchOddsTime'] >= self.start) & (eventId.pricesPlusOneToAway['matchOddsTime'] < self.end)
                    
#                     self.sampleMatchPrices = eventId.prices.loc[self.mask].resample('S', on='matchOddsTime')['homeBackPrice', 'homeLayPrice', 'awayBackPrice', 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'].mean()
#                     self.sampleHomePlusOne = eventId.pricesPlusOneToHome.loc[self.maskHomePlusOne].resample('S', on='matchOddsTime')[f'{eventId.homeTeam}_back', f'{eventId.homeTeam}_lay', f'{eventId.awayTeam}_back', f'{eventId.awayTeam}_lay', 'drawBackPrice', 'drawLayPrice'].mean()
#                     self.sampleAwayPlusOne = eventId.pricesPlusOneToAway.loc[self.maskAwayPlusOne].resample('S', on='matchOddsTime')[f'{eventId.awayTeam}_back', f'{eventId.awayTeam}_lay', f'{eventId.homeTeam}_back', f'{eventId.homeTeam}_lay', 'drawBackPrice', 'drawLayPrice'].mean()
                
#                     self.homeBackAverage = self.sampleMatchPrices.iloc[-10:-1]['homeBackPrice'].mean()
#                     self.awayBackAverage = self.sampleMatchPrices.iloc[-10:-1]['awayBackPrice'].mean()
                    
#                     self.homeUpperBand = eventId.bollingerBandDict[f'{str(self.interval)}'].iloc[-1:]['homeUpperBand'].values[0]
#                     self.awayUpperBand = eventId.bollingerBandDict[f'{str(self.interval)}'].iloc[-1:]['awayUpperBand'].values[0]
   
#                     self.minOfIntervalStart = math.ceil(((self.sampleMatchPrices.iloc[0:1].index - matchStartTime).values[0]).astype('float64')/1e9/60)
                    
#                     self.xgsForPeriod = xgForPeriod(self)
#                     self.plusOneMovingAverages = plusOneMovingAverage(self)
#                     self.goalPriceMovements = pricesAtPeriodStart(self)
                    
#                     ''' Lay bet placed on home team '''
#                     self.homeLay_homeGoal = profitOrLossIfGoal(self, self.sampleHomePlusOne, eventId.homeTeam, 'homeLayPrice')
#                     self.homeLay_awayGoal = profitOrLossIfGoal(self, self.sampleAwayPlusOne, eventId.homeTeam, 'homeLayPrice')
                    
#                     ''' Lay bet placed on away team '''
#                     self.awayLay_homeGoal = profitOrLossIfGoal(self, self.sampleHomePlusOne, eventId.awayTeam, 'awayLayPrice')
#                     self.awayLay_awayGoal = profitOrLossIfGoal(self, self.sampleAwayPlusOne, eventId.awayTeam, 'awayLayPrice')
                           
#                     self.totalLossHomeLay = averageLossForPeriodHomeLay(self.xgsForPeriod, self.homeLay_homeGoal, self.homeLay_awayGoal).values
#                     self.totalLossAwayLay = averageLossForPeriodAwayLay(self.xgsForPeriod, self.awayLay_homeGoal, self.awayLay_awayGoal).values

#                     self.bollingerBandDataframe = bollingerBands(self)
#                     self.breakEvenPriceHomeLay = breakEvenCalcsHomeLay(self)
#                     self.breakEvenPriceAwayLay = breakEvenCalcsAwayLay(self)
                    
#                     self.homeLayOpportunity = checkForOpportunity(self, self.homeBackAverage, self.priceHomeLay, self.homeUpperBand, 'homeBackPrice', 'homeMovingAverage', 'awayBackPrice')
#                     self.awayLayOpportunity = checkForOpportunity(self, self.awayBackAverage, self.priceAwayLay, self.awayUpperBand, 'awayBackPrice', 'awayMovingAverage', 'homeBackPrice')
        
#                     # if self.homeLayOpportunity == False:
#                     #     Betting(1.226299557, 'ALL').getMarketBets()
        
#         def checkForOpportunity(self, teamBackAverage, priceTeamLay, teamUpperBand, teamBackPrice, teamMovingAverage, otherTeamBackPrice):
#             if placeBetCalcs(teamBackAverage, priceTeamLay) == True:
#                 if otherTeamPriceGradient(otherTeamBackPrice) == True:
#                     if teamVolatility(teamBackAverage, teamUpperBand) == True:   
#                         if priceSpikes(self, teamBackAverage, teamBackPrice, teamMovingAverage) == True:
#                             print('It worked')      
#                             return True
#             return False

#         def xgForPeriod(self):
#             # Calculate the xg at the start and end of the interval to get the expected goals during that period
#             self.homeXgForPeriod = (xGRemaining(self.homeXg, self.minOfIntervalStart)) - xGRemaining(self.homeXg, self.minOfMatch)
#             self.awayXgForPeriod = (xGRemaining(self.awayXg, self.minOfIntervalStart)) - xGRemaining(self.awayXg, self.minOfMatch)
#             print(self.homeXgForPeriod, self.awayXgForPeriod)
#             return self.homeXgForPeriod, self.awayXgForPeriod
        
#         def xGRemaining(xg, minOfMatch):
#             return ((1-((1/95*minOfMatch))**.84) * xg)
        
#         def plusOneMovingAverage(self):
#             self.movingAveragePlusOneToHome_homeBack = self.sampleHomePlusOne.iloc[0:-1][f'{eventId.homeTeam}_back'].mean()
#             self.movingAveragePlusOneToHome_awayBack = self.sampleHomePlusOne.iloc[0:-1][f'{eventId.awayTeam}_back'].mean()
#             self.movingAveragePlusOneToHome_drawBack = self.sampleHomePlusOne.iloc[0:-1]['drawBackPrice'].mean()
            
#             self.movingAveragePlusOneToHome_homeLay = self.sampleHomePlusOne.iloc[0:-1][f'{eventId.homeTeam}_lay'].mean()
#             self.movingAveragePlusOneToHome_awayLay = self.sampleHomePlusOne.iloc[0:-1][f'{eventId.awayTeam}_lay'].mean()
#             self.movingAveragePlusOneToHome_drawLay = self.sampleHomePlusOne.iloc[0:-1]['drawLayPrice'].mean()
            
#             return self.movingAveragePlusOneToHome_homeBack, self.movingAveragePlusOneToHome_awayBack, self.movingAveragePlusOneToHome_drawBack, \
#                     self.movingAveragePlusOneToHome_homeLay, self.movingAveragePlusOneToHome_awayLay, self.movingAveragePlusOneToHome_drawLay
        
#         def pricesAtPeriodStart(self):
#             self.homeStartBackPrice = self.sampleMatchPrices.iloc[0:1]['homeBackPrice']
#             self.awayStartBackPrice = self.sampleMatchPrices.iloc[0:1]['awayBackPrice']
#             self.drawStartBackPrice = self.sampleMatchPrices.iloc[0:1]['drawBackPrice']
#             return self.homeStartBackPrice, self.awayStartBackPrice, self.drawStartBackPrice
            
#         def profitOrLossIfGoal(self, plusOneMarket, team, pricesDfColumn):
#             x = plusOneMarket.iloc[-1][f'{team}_back']-1
#             y = self.sampleMatchPrices.iloc[0:1][pricesDfColumn]-1
#             z = plusOneMarket.iloc[-1][f'{team}_back']
#             ''' Example
#             x = self.sampleHomePlusOne.iloc[-1][f'{eventId.homeTeam}_back']-1
#             y = self.sampleMatchPrices.iloc[0:1]['homeLayPrice']-1
#             z = self.sampleHomePlusOne.iloc[-1][f'{eventId.homeTeam}_back']
#             '''
#             return (x - y) / z
            
#         def averageLossForPeriodHomeLay(xgsForPeriod, homeLay_homeGoal, homeLay_awayGoal):
#             return xgsForPeriod[0]*homeLay_homeGoal + xgsForPeriod[1]*homeLay_awayGoal
        
#         def averageLossForPeriodAwayLay(xgsForPeriod, awayLay_homeGoal, awayLay_awayGoal):
#             return xgsForPeriod[0]*awayLay_homeGoal + xgsForPeriod[1]*awayLay_awayGoal
        
#         def bollingerBands(self):
#             self.bollingerBandDataframe = eventId.bollingerBandDict[f'{str(self.interval)}']
#             return self.bollingerBandDataframe
 
#         def breakEvenCalcsHomeLay(self):         
#             self.breakEvenHomeLay = self.totalLossHomeLay
#             self.priceHomeLay = self.sampleMatchPrices.iloc[0:1]['homeBackPrice']
#             self.initialPrice = self.sampleMatchPrices.iloc[0:1]['homeBackPrice'] # Price at the start of the interval
#             while self.breakEvenHomeLay[0] < 0:
#                 self.breakEvenHomeLay += 0.01 / 60
#                 self.breakEvenHomeLay = self.breakEvenHomeLay + (((self.HomeLay-1) - (self.initialPrice-1)) / self.HomeLay)
#             return self.breakEvenHomeLay
        
#         def breakEvenCalcsAwayLay(self):
#             self.breakEvenAwayLay = self.totalLossAwayLay
#             self.priceAwayLay = self.sampleMatchPrices.iloc[0:1]['awayBackPrice']
#             self.initialPrice = self.sampleMatchPrices.iloc[0:1]['awayBackPrice'] # Price at the start of the interval
#             while self.breakEvenAwayLay[0] < 0:
#                 self.priceAwayLay += 0.01 / 60
#                 self.breakEvenAwayLay = self.breakEvenAwayLay + (((self.AwayLay-1) - (self.initialPrice-1)) / self.AwayLay)
#             return self.priceAwayLay
                
#         def placeBetCalcs(teamBackAverage, priceTeamLay):
#             if teamBackAverage - priceTeamLay.values[0] < 0:
#                 # return True
#                 return False
#             if teamBackAverage - priceTeamLay.values[0] >= 0:
#                 return True

#         def otherTeamPriceGradient(teamBackPrice):
#             teamGradientRange = eventId.prices.loc[self.mask].resample('S', on='matchOddsTime')['matchOddsTime',f'{teamBackPrice}'].mean()
#             teamGradient = (teamGradientRange.iloc[-1:][f'{teamBackPrice}'].values[0] - teamGradientRange.iloc[0:1][f'{teamBackPrice}'].values[0]) / \
#                             (teamGradientRange.iloc[-1:]['matchOddsTime'].values[0] - teamGradientRange.iloc[0:1]['matchOddsTime'].values[0]).astype('float64')/1e9/60
#             if teamGradient < 0:
#                 return True
#             # return True
#             return False

#         def teamVolatility(teamBackAverage, teamUpperBand):
#             if teamBackAverage < teamUpperBand:
#                 return True
#             # return True
#             return False

#         def priceSpikes(self, teamBackAverage, teamBackPrice, teamMovingAverage):
#             spikePriceUp = teamBackAverage * 1.15
#             spikePriceDown = teamBackAverage * 0.85
#             # Get the min and max prices during the interval
#             minPrice = self.sampleMatchPrices[f'{teamBackPrice}'].min()
#             maxPrice = self.sampleMatchPrices[f'{teamBackPrice}'].max()
            
#             if maxPrice > spikePriceUp or minPrice < spikePriceDown:
#                 return False
#             if self.sampleMatchPrices.iloc[-1:][f'{teamBackPrice}'].values[0] < self.bollingerBandDataframe.iloc[-1:][f'{teamMovingAverage}'].values[0]:
#                 return False
#             return True

#         goalCalculations(self, eventId, intervals)
        

intervals = [10,300,360,420,480,540,600,660,720,780,840,960,1020,1080,1140,1200]            
# matchObjectsList = matchObjects(betAngelApiObject)

