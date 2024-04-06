from threading import Thread, Event
# import concurrent.futures

from queue import Queue

from time import sleep, time

from datetime import datetime

from callRapidApi import CallRapidApi
from callBetfair import CallBetfair
from match import Match
from bollingerBands import BollingerBands
from calculations import Calculations
from matchPrices import MatchPrices, MatchOddsPlusOne
from betting import Betting
from rapidApi import updateRapidApiInfo

from workerFunctions import *

from teamsCountries import *





def todaysDate():
    now = datetime.now().date()
    return now

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
# Create a match object for each match/event loaded into Bet Angel
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


class PeriodicThread(Thread):

    def __init__(self, main, interval):
        self.stop_event = Event()
        self.interval = interval
        self.main = main
        super(PeriodicThread, self).__init__()
    
    def run(self):
         while not self.stop_event.is_set():
             self.main()
             self.stop_event.wait(self.interval)        
   
    def terminate(self):
        self.stop_event.set()
    
    
''' Daily tasks that only need to be done once'''
def workerFunction0():
    # Call Rapid Api to get todays fixtures and add Rapid Api event id to match objects.
    for league in leagues:   
        result = CallRapidApi(today, league, '2023').todaysFixtures()['response']
        for i in range(0, len(result)):
            
            country = result[i]['league']['country']
            teamsInCountry = teams[f'{country}']
            rapidApiHomeTeam = teamsInCountry[result[i]['teams']['home']['name']]
            rapidApiAwayTeam = teamsInCountry[result[i]['teams']['away']['name']]

            for match in matchObjectsList:
                if match.homeTeam.lower() == rapidApiHomeTeam.lower() and match.awayTeam.lower() == rapidApiAwayTeam.lower():
                    match.rapidApiId = result[i]['fixture']['id']
                    match.matchStatus = result[i]['fixture']['status']['short']
                    match.homeTeamRapidApi = result[i]['teams']['home']['name']
                    match.awayTeamRapidApi = result[i]['teams']['away']['name']
                    break
    
    
    
def betfairInPlayStatus(betAngelApiObject, matchObjectsList):
    apiCallResult = betAngelApiObject.markets()
    for result in apiCallResult:
        for match in matchObjectsList:
            if result['eventId'] == match.eventId:
                match.isInPlay = result['inPlay']
                break
    return
    
                      
''' Continously updates prices and bollinger data '''
def workerFunction1():

    now = datetime.now().replace(microsecond=0)
    ''' DO NOT DELETE THIS - uncomment for production '''
    betfairInPlayStatus(betAngelApiObject, matchObjectsList)
    
  
    MatchPrices(now, betAngelApiObject, matchObjectsList)
    MatchOddsPlusOne(now, betAngelApiObject, matchObjectsList)
    for match in matchObjectsList:
        
        BollingerBands(match, intervals)
        Calculations(match, intervals, betAngelApiObject, matchObjectsList, now)
    
        # if calcInstance.checkOpportunityValue()[0] == True and calcInstance.checkOpportunityValue()[0] == False:
        #     stakesValues = Calculations.calculateStake('home', match.fixture, match.dateTimeObject, calcInstance)    
                   
        # elif calcInstance.checkOpportunityValue()[0] == False and calcInstance.checkOpportunityValue()[0] == True:
        #     stakesValues = Calculations.calculateStake('away', match.fixture, match.dateTimeObject)
             
        # else:
        #     continue      
                
          
      
''' Update xg attributes when a market has less than 120 seconds until start time'''
def workerFunction2():
    for match in matchObjectsList:
        if (match.dateTimeObject - datetime.now()).total_seconds() < 120000000: # Change this back to 120
            match.getXg()


# ''' Scores from Rapid Api'''
def workerFunction3():
    
    updateRapidApiInfo(leagues, today, CallRapidApi, matchObjectsList)
    

''' Print score, minute and prices to console '''
def workerFunction4():    
    print('-----------------')
    print(matchObjectsList)
    for match in matchObjectsList:
        try:
            print(match.fixture, match.matchStatus, match.homeGoals, match.awayGoals, match.homeGoalsList, match.awayGoalsList, match.prices.iloc[-1]['homeBackPrice'], match.prices.iloc[-1]['awayBackPrice'], match.prices.iloc[-1]['drawBackPrice'])               
        except IndexError:
            print(f'Match not started {match.fixture}')
            continue
        
leagues = [39,40,41,61,78,135,140,141,144,88,141,136,62,79,94,188,113,207,119,307,253,71,128] # Don't forget Champions League and internationals etc
today = todaysDate()
              
if __name__ == '__main__':
    
    intervals = [10,300,360,420,480,540,600,660,720,780,840,960,1020,1080,1140,1200]
   
    betAngelApiObject = createBetAngelApiObject()
    matchObjectsList = matchObjects(betAngelApiObject)
    
    workerFunction0()
    workerFunction3()

    worker1 = PeriodicThread(workerFunction1, interval=0.25)
    worker1.start()
    
    worker2 = PeriodicThread(workerFunction2, interval=60)
    worker2.start()
    
    worker3 = PeriodicThread(workerFunction3, interval=1)
    worker3.start()
    
    worker4 = PeriodicThread(workerFunction4, interval=15)
    worker4.start()


    try:
       # this is to keep the main thread alive
       while True:
           sleep(1)
    except (KeyboardInterrupt, SystemExit):
        
        worker1.terminate()
        worker2.terminate()
        worker3.terminate()
        worker4.terminate()