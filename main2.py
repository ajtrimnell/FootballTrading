import threading 
import concurrent.futures

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

# worker1 = PeriodicThread(workerFunction1, interval=0.25, args=[superLst])
# class PeriodicThread(threading.Thread):

#     def __init__(self, main, interval):
#         self.stop_event = threading.Event()
#         self.interval = interval
#         self.main = main()
#         super(PeriodicThread, self).__init__()
    
#     def run(self):
#          while not self.stop_event.is_set():
#              self.main()
#              self.stop_event.wait(self.interval)        
   
#     def terminate(self):
#         self.stop_event.set()
    
    
''' Daily tasks that only need to be done once'''
def workerFunction0():
    # Call Rapid Api to get todays fixtures and add Rapid Api event id to match objects.
    for league in leagues:   
        result = CallRapidApi(today, league, '2023').todaysFixtures()['response']
        for i in range(0, len(result)):
            country = result[i]['league']['country']
            teamsInCountry = teams[f'{country}']
            rapidApiHomeTeam = teamsInCountry[result[i]['teams']['home']['name']].lower()
            rapidApiAwayTeam = teamsInCountry[result[i]['teams']['away']['name']].lower()

            for match in matchObjectsList:
                if match.homeTeam.lower() == rapidApiHomeTeam and match.awayTeam.lower() == rapidApiAwayTeam:
                    match.rapidApiId = result[i]['fixture']['id']
                    match.matchStatus = result[i]['fixture']['status']['short']
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
def workerFunction1(sleepTime, superLst):
    sleep(sleepTime)

    now = datetime.now().replace(microsecond=0)
    # betfairInPlayStatus(betAngelApiObject, matchObjectsList)
    
    # superLst = args[0]
    print(len(superLst))
    for result in superLst:
        
        for i in range(0, len(result)):   
            rapidApiEventId = result[i]['fixture']['id']
            for match in matchObjectsList:
                if match.rapidApiId == rapidApiEventId:
                    
                    match.matchScoreList.append(((datetime.now().replace(microsecond=0), result[i]['goals']['home'], result[i]['goals']['away'])))
                    match.matchStatus = result[i]['fixture']['status']['short']
                    
                    homeGoals = result[i]['goals']['home']
                    awayGoals = result[i]['goals']['away']
                    goalCount = int(homeGoals) + int(awayGoals)
                    
                    match.homeGoals = homeGoals
                    match.awayGoals = awayGoals
                    match.goalCount = goalCount
                    
                    if len(match.homeGoalsTimes) + len(match.awayGoalsTimes) != goalCount:
                        getGoalTimes(match, result[i]['events'])
                    break
  
  
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


def getGoalTimes(match, result):
    for event in result:
        if event['type'] == "Goal"  and event['detail'] != "Missed Penalty":
            if match.homeTeam == event['team']['name']:
                goalTimesDict = match.goalTimesDict.get(f'{match.homeTeam}')
                minOfGoal = event['time']['elapsed']
                if minOfGoal in goalTimesDict:
                    continue
                else:
                    match.goalTimesDict.get(f'{match.homeTeam}').append(minOfGoal)
                    continue
                
            if match.awayTeam == event['team']['name']:
                goalTimesDict = match.goalTimesDict.get(f'{match.awayTeam}')
                minOfGoal = event['time']['elapsed']
                if minOfGoal in goalTimesDict:
                    continue
                else:
                    match.goalTimesDict.get(f'{match.awayTeam}').append(minOfGoal)
                    continue
    return
                
    


''' Scores from Rapid Api'''
def workerFunction3(superLst, sleepTime):
    # sleepTime = args[0]
    sleep(sleepTime)
    # workerFunctionX(CallRapidApi, today, matchObjectsList, betAngelApiObject, leagues)
    # def workerFunctionX(CallRapidApi, today, matchObjectsList, betAngelApiObject, leagues):
    
    # betfairInPlayStatus(betAngelApiObject, matchObjectsList)
    # Call Rapid Api to get the current goals for each team and update the match objects.
    # Rapid Api event id is used as the identifier to find the correct match object.

    # superLst = args[0]
    superLstTemp = []
    for league in leagues:
        resultTemp = CallRapidApi(today, league, '2023').inplayMatches()['response']
        superLstTemp.append(resultTemp)
 
    superLst = superLstTemp
    return superLst

    # for result in superLst:
    #     # print(type(lst), type(result), len(lst), len(result))
    #     for i in range(0, len(result)):
    #         rapidApiEventId = result[i]['fixture']['id']
    #         for match in matchObjectsList:
    #             if match.rapidApiId == rapidApiEventId:
    #                 match.matchScoreList.append(((datetime.now().replace(microsecond=0), result[i]['goals']['home'], result[i]['goals']['away'])))
    #                 match.matchStatus = result[i]['fixture']['status']['short']
                    
    #                 homeGoals = result[i]['goals']['home']
    #                 awayGoals = result[i]['goals']['away']
    #                 goalCount = int(homeGoals) + int(awayGoals)
                    
    #                 match.homeGoals = homeGoals
    #                 match.awayGoals = awayGoals
    #                 match.goalCount = goalCount
                    
    #                 if len(match.homeGoalsTimes) + len(match.awayGoalsTimes) != goalCount:
    #                     getGoalTimes(match, result[i]['events'])
    #                 break
    return 0


''' Print score, minute and prices to console '''
def workerFunction4():    
    print('-----------------')
    print(matchObjectsList)
    for match in matchObjectsList:
        try:
            print(match.fixture, match.matchStatus, match.homeGoals, match.awayGoals, match.goalTimesDict, match.prices.iloc[-1]['homeBackPrice'], match.prices.iloc[-1]['awayBackPrice'], match.prices.iloc[-1]['drawBackPrice'])               
        except IndexError:
            print(f'Match not started {match.fixture}')
            continue
        
leagues = [39,40,41,61,78,135,140,141,144,88,141,136,62,79,94,188,113,207,119,307,253,71,128] # Don't forget Champions League and internationals etc
today = todaysDate()
              
if __name__ == '__main__':
    
    intervals = [10,300,360,420,480,540,600,660,720,780,840,960,1020,1080,1140,1200]
    superLst = []   
    betAngelApiObject = createBetAngelApiObject()
    matchObjectsList = matchObjects(betAngelApiObject)
    
    # worker0 = PeriodicThread(workerFunction0, interval=1)
    # worker0.start()
    workerFunction0()
    workerFunction3(superLst, 15)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        
        try:
        # this is to keep the main thread alive
            while True:
        
        
                worker1 = executor.submit(workerFunction1, 0.25, superLst)
                worker3 = executor.submit(workerFunction3, superLst, 15)
        
        
        # try:
        # # this is to keep the main thread alive
        #     while True:
        #         sleep(1)
        except (KeyboardInterrupt, SystemExit):

                #     # worker0.terminate()
            worker1.terminate()
    #     # worker2.terminate()
            worker3.terminate()
    #     # worker4.terminate()
        
            
            
            
        
    
    # worker4 = PeriodicThread(workerFunction4, interval=15)
    # worker4.start()
    
       
    # try:
    #    # this is to keep the main thread alive
    #    while True:
    #        sleep(1)
    # except (KeyboardInterrupt, SystemExit):
        
    #     # worker0.terminate()
    #     worker1.terminate()
    #     # worker2.terminate()
    #     worker3.terminate()
    #     # worker4.terminate()