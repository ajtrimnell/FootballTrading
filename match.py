import pandas as pd
import numpy as np
from datetime import datetime

from teamsCountries import *

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
        
        self.homeBetfairId = None
        self.awayBetfairId = None
        self.drawBetfairId = None
        
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
        
        ''' Betting '''
        self.numberOfBetsPlaced = 0

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
            self.homeBetfairId = selections[0].get('id')
            self.homeTeam = selections[0].get('name')
            self.awayId = selections[1].get('id')
            self.awayTeam = selections[1].get('name')
            self.drawBetfairId = selections[2].get('id')
            return self.homeBetfairId, self.homeTeam, self.awayBetfairId, self.awayTeam, self.drawBetfairId
        
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
            
        def bollingerBandsDataframeDict(self):        
            self.bollingerBandDict = {
                '10':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
                '300':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
                '360':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
                '420':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
                '480':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
                '540':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
                '600':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
                '600':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
                '660':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
                '720':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
                '780':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
                '840':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
                '900':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
                '960':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
                '1020':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
                '1080':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
                '1140':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
                '1200':pd.DataFrame(columns=['rowIndex', 'matchTime', 'homeMovingAverage', 'homeOneStandardDev', 'homeUpperBand', 'homeLowerBand', 'homeUpperStd', 'homeLowerStd',
                                           'awayMovingAverage', 'awayOneStandardDev', 'awayUpperBand', 'awayLowerBand', 'awayUpperStd', 'awayLowerStd']),
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
        bollingerBandsDataframeDict(self)
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