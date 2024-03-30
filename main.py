from threading import Thread, Event
from time import sleep
from datetime import datetime

from callBetAngelApi import *
from callRapidApi import *
from callBetfair import CallBetfair
from match import Match
from bollingerBands import BollingerBands

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

betAngelApiObject = createBetAngelApiObject()
matchObjectsList = matchObjects(betAngelApiObject)


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
        result = RapidApi(today, league, '2023').todaysFixtures()['response']
        for i in range(0, len(result)):
            country = result[i]['league']['country']
            teamsInCountry = teams[f'{country}']
            rapidApiHomeTeam = teamsInCountry[result[i]['teams']['home']['name']]
            rapidApiAwayTeam = teamsInCountry[result[i]['teams']['away']['name']]

            for match in matchObjectsList:
                if match.homeTeam == rapidApiHomeTeam and match.awayTeam == rapidApiAwayTeam:
                    match.rapidApiId = result[i]['fixture']['id']
                    break
                      
''' Continously updates prices data '''
def workerFunction1():
    # Stating a class name and the putting () after it will create an instance of that class.
    now = datetime.now().replace(microsecond=0)
    MatchPrices(now)
    MatchOddsPlusOne(now)
    for match in matchObjectsList:
        BollingerBands(match, intervals)
        Calculations(match, intervals)

# ''' Continously updates bollinger data '''
# def workerFunction1a():
#     # Stating a class name and the putting () after it will create an instance of that class.
#     # now = datetime.now().replace(microsecond=0)
#     # MatchPrices(now)
#     # MatchOddsPlusOne(now)
#     for match in matchObjectsList:
#         BollingerBands(match, intervals)
#         Calculations(match, intervals)
        
''' Update xg attributes when a market has less than 120 seconds until start time'''
def workerFunction2():
    for match in matchObjectsList:
        if (match.dateTimeObject - datetime.now()).total_seconds() < 120000: # Change this back to 120
            match.getXg()

''' Scores from Rapid Api'''
def workerFunction3():
    # Call Rapid Api to get the current goals for each team and update the match objects.
    # Rapid Api event id is used as the identifier to find the correct match object.
    for league in leagues:
        result = RapidApi(today, league, '2023').inplayMatches()['response']
        for i in range(0, len(result)):
            rapidApiEventId = result[i]['fixture']['id']
            for match in matchObjectsList:
                if match.rapidApiId == rapidApiEventId:
                    match.homeGoals = result[i]['goals']['home']
                    match.awayGoals = result[i]['goals']['away']
                    break
   
''' Print score, minute and prices to console '''
def workerFunction4():    
    print('-----------------')
    for match in matchObjectsList:
        try:
            print(match.fixture, match.homeGoals, match.awayGoals, match.prices.iloc[-1]['homeBackPrice'], match.prices.iloc[-1]['awayBackPrice'], match.prices.iloc[-1]['drawBackPrice'])               
        except IndexError:
            print(f'IndexError on {match.fixture}')
            continue
        
leagues = [39,40,41,61,78,135,140] # Don't forget Champions League and internationals etc
today = todaysDate()
              
if __name__ == '__main__':
    
    # worker0 = PeriodicThread(workerFunction0, interval=1)
    # worker0.start()
    workerFunction0()
    
    
    worker1 = PeriodicThread(workerFunction1, interval=0.25)
    worker1.start()
    
    # worker1a = PeriodicThread(workerFunction1a, interval=0.25)
    # worker1a.start()
       
    worker2 = PeriodicThread(workerFunction2, interval=60)
    worker2.start()
          
    worker3 = PeriodicThread(workerFunction3, interval=15)
    # worker3.start()
    
    worker4 = PeriodicThread(workerFunction4, interval=1)
    worker4.start()
   
          
    try:
       # this is to keep the main thread alive
       while True:
           sleep(1)
    except (KeyboardInterrupt, SystemExit):
        
        # worker0.terminate()
        worker1.terminate()
        # worker1a.terminate()
        worker2.terminate()
        worker3.terminate()
        worker4.terminate()