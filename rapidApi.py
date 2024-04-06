from datetime import datetime
import pandas as pd
import json

def getGoalTimes(match, result):
    
    # goalTimesDict = {match.homeTeam:[], match.awayTeam:[]}
    homeGoalsList = {match.homeTeam:[]}
    awayGoalsList = {match.awayTeam:[]}
    
    for event in result:
        if event['type'] == "Goal"  and event['detail'] != "Missed Penalty":
            if match.homeTeamRapidApi == event['team']['name']:
                minOfGoal = event['time']['elapsed']
                homeGoalsList.get(f'{match.homeTeam}').append(minOfGoal)
                continue
                
            if match.awayTeamRapidApi == event['team']['name']:
                minOfGoal = event['time']['elapsed']
                awayGoalsList.get(f'{match.awayTeam}').append(minOfGoal)
                continue
                 
    return homeGoalsList, awayGoalsList


''' Scores from Rapid Api'''
def updateRapidApiInfo(leagues, today, CallRapidApi, matchObjectsList):
    
    for league in leagues:   
        result = CallRapidApi(today, league, '2023').inplayMatches()['response']    
        for i in range(0, len(result)):  
            if len(result[i]) == 0:
                print('Result length is 0')
                continue     
            else:      
                rapidApiEventId = result[i]['fixture']['id']
                for match in matchObjectsList:
                    if match.rapidApiId == rapidApiEventId:
                                    
                        fixture = match.fixture
                        homeGoals = result[i]['goals']['home']
                        awayGoals = result[i]['goals']['away']
                        goalCount = int(homeGoals) + int(awayGoals)

                        dictObject = {'fixture':match.fixture,
                                      'dateTime':str(datetime.now().replace(microsecond=0)),
                                      'matchStatus':result[i]['fixture']['status']['short'],
                                      'homeGoals':homeGoals,
                                      'awayGoals':awayGoals,
                                      'goalCount':goalCount,
                                      'homeGoalsList':getGoalTimes(match, result[i]['events'])[0],
                                      'awayGoalsList':getGoalTimes(match, result[i]['events'])[1]
                                     }
                        
                        jsonObject = json.dumps(dictObject)
                        
                        with open(f'C:/dev/Python/betfairData/rapidApiDataCsvs/{fixture}.json', 'w') as outfile:
                            outfile.write(jsonObject)
                        
                        outfile.close()
                        
                        
                        # ListForCsv.append(match.fixture)
                        # ListForCsv.append(datetime.now().replace(microsecond=0))
                        # ListForCsv.append(result[i]['fixture']['status']['short'])
                        # ListForCsv.append(homeGoals)
                        # ListForCsv.append(awayGoals)
                        # ListForCsv.append(goalCount)
                        # ListForCsv.append(getGoalTimes(match, result[i]['events'])[0])
                        # ListForCsv.append(getGoalTimes(match, result[i]['events'])[1])

                        # df = pd.DataFrame([ListForCsv], columns=['fixture', 'dateTime', 'matchStatus', 'homeGoals', 'awayGoals',\
                        #                                          'goalCount', 'homeGoalsList', 'awayGoalsList'])
                        
                        # # df.to_csv(f'C:/dev/Python/betfairData/rapidApiDataCsvs/{fixture}.csv')
                        
                        # file = open(f'C:/dev/Python/betfairData/rapidApiDataCsvs/{fixture}.json', mode='w')
                        
                        # df.to_json(f'C:/dev/Python/betfairData/rapidApiDataCsvs/{fixture}.json', orient='records', lines=True)
    
    return

# ''' Update Match object with Rapid Api data - scores, status, goals times '''
# def updateMatchObject(match):
    
#     # file = open(f'C:/dev/Python/betfairData/rapidApiDataCsvs/{match.fixture}.json')
#     # content = json.load(file) 
#     # file.close()
    
#     with open(f'C:/dev/Python/betfairData/rapidApiDataCsvs/{match.fixture}.json', 'r') as file:
#         content = json.load(file) 

#         match.matchStatus = content['matchStatus']
#         match.homeGoals = content['homeGoals']
#         match.awayGoals = content['awayGoals']
#         match.homeGoalsList = content['homeGoalsList']
#         match.awayGoalsList = content['awayGoalsList']
#         match.goalCount = content['goalCount']
    
#         file.close()
    
#         return