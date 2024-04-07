from datetime import datetime
import pandas as pd
import json

def getGoalTimes(match, result):
    
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
                        
                        with open(f'C:/dev/Python/betfairData/rapidApiDataCsvs/{match.homeTeam} v {match.awayTeam}.json', 'w') as outfile:
                            outfile.write(jsonObject)
                        
                        outfile.close()
    
    return
